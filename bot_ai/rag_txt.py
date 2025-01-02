import os
import time
import uuid
from datetime import datetime
from io import BytesIO
from itertools import islice

import numpy as np
import pandas as pd
import pdfplumber
import tiktoken
import vertexai
from google.cloud import bigquery
from google.cloud import storage
from vertexai.language_models import TextEmbeddingModel

from app.bot_ai.bot_multi_model import VertexAImultimodel


class RAG_txt:  # noqa: N801
    EMBEDDING_CTX_LENGTH = 512
    EMBEDDING_ENCODING = "cl100k_base"
    BATCH_SIZE = 5
    PROJECT_ID = "lumi-app-433302"
    LOCATION = "us-central1"
    UID = datetime.now().strftime("%m%d%H%M")  # noqa: DTZ005

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/bot_ai/gcp_credentials.json"
        self.storage_client = storage.Client()
        self.bq_client = bigquery.Client()
        vertexai.init(project=self.PROJECT_ID, location=self.LOCATION)
        self.vx_model = VertexAImultimodel()
        self.chat, self.model = self.vx_model.start_chat()
        self.embedding_model = TextEmbeddingModel.from_pretrained(
            "text-multilingual-embedding-002",
        )

    def generate_embeddings(self, texts, model):
        embs = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            time.sleep(1)
            result = model.get_embeddings(texts[i : i + self.BATCH_SIZE])
            embs = embs + [e.values for e in result]  # noqa: PD011
        return embs

    def batched(self, iterable, n):
        """Batch data into tuples of length n. The last batch may be shorter."""
        if n < 1:
            raise ValueError("n must be at least one")  # noqa: EM101, TRY003
        it = iter(iterable)
        while batch := tuple(islice(it, n)):
            yield batch

    def chunked_tokens(self, text, chunk_length, encoding_name="cl100k_base"):
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        yield from self.batched(tokens, chunk_length)

    def len_safe_get_embedding(
        self,
        text,
        model,
        max_tokens=EMBEDDING_CTX_LENGTH,
        encoding_name=EMBEDDING_ENCODING,
    ):
        # Initialize lists to store embeddings and corresponding text chunks
        chunk_texts = []
        # Iterate over chunks of tokens from the input text
        for chunk in self.chunked_tokens(
            text,
            chunk_length=max_tokens,
            encoding_name=encoding_name,
        ):
            txt = tiktoken.get_encoding(encoding_name).decode(chunk)
            chunk_texts.append(txt)

        # Generate embeddings for each chunk and append to the list
        chunk_embeddings = self.generate_embeddings(texts=chunk_texts, model=model)
        # Return the list of chunk embeddings and the corresponding text chunks
        return chunk_embeddings, chunk_texts

    def chunking_n_vectorization(self, file_dict, model):
        vector_store = pd.DataFrame(columns=["id", "name", "text", "embedding"])
        for name, blob in file_dict.items():
            pdf_data = blob.download_as_bytes()
            if len(pdf_data) < 5:  # noqa: PLR2004
                continue
            with pdfplumber.open(BytesIO(pdf_data)) as pdf:
                text = "".join(page.extract_text() for page in pdf.pages)
            chunk_embeddings, chunk_texts = self.len_safe_get_embedding(
                text,
                model=model,
            )
            ids = [str(uuid.uuid4()) for _ in range(len(chunk_embeddings))]
            name_lst = [name] * len(chunk_embeddings)
            vector_store = pd.concat(
                [
                    vector_store,
                    pd.DataFrame(
                        {
                            "id": ids,
                            "name": name_lst,
                            "text": chunk_texts,
                            "embedding": chunk_embeddings,
                        },
                    ),
                ],
            )
        return vector_store

    def embeddings_bucket2bigquery(self, bucket_name, prefix, table_name):
        blobs = self.storage_client.list_blobs(bucket_name, prefix=prefix)
        files = {blob.name.split("/")[-1]: blob for blob in blobs}

        vector_store = self.chunking_n_vectorization(
            files,
            model=self.embeddings_model,
        ).reset_index(drop=True)

        try:
            self.bq_client.get_table(table_name)
        except Exception:  # noqa: BLE001
            self.bq_client.create_table(table_name)

        job_config = bigquery.LoadJobConfig(
            # Specify a schema. The schema is used to assist in data type definitions.
            schema=[
                # Specify the type of columns whose type cannot be auto-detected. For
                # example the "title" column uses pandas dtype "object", so its
                # data type is ambiguous.
                bigquery.SchemaField("id", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("name", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("text", bigquery.enums.SqlTypeNames.STRING),
                bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
            ],
            # BigQuery appends loaded rows to an existing table by default,
            # but with WRITE_TRUNCATE write disposition it replaces the table
            # with the loaded data.
            write_disposition="WRITE_TRUNCATE",
        )

        job = self.bq_client.load_table_from_dataframe(
            vector_store,
            table_name,
            job_config=job_config,
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

    def homemade_vector_search(
        self,
        prompt,
        vector_store,
        distance_metric="euclidean",
        neighbors=5,
    ):
        vs_matrix = np.vstack(vector_store["embedding"].values.tolist())  # noqa: PD011

        q_emb = np.array(self.generate_embeddings([prompt], self.embedding_model))

        distance_functions = {
            "manhattan": lambda a, b: np.linalg.norm(a - b, ord=1, axis=1),
            "euclidean": lambda a, b: np.linalg.norm(a - b, axis=1),
            "cosine": lambda a, b: 1
            - ((a @ b.T) / (np.linalg.norm(a) * np.linalg.norm(b, axis=1)))[0],
            "dot": lambda a, b: 1 - (a @ b.T)[0],
        }

        if distance_metric not in [*list(distance_functions.keys()), "all"]:
            raise ValueError(f"Invalid distance metric: {distance_metric}")  # noqa: TRY003, EM102

        if distance_metric == "all":
            distance_metric = distance_functions.keys()
        else:
            distance_metric = [distance_metric]

        ensemble = []
        N = neighbors  # noqa: N806

        for x in distance_metric:
            distances = distance_functions[x](q_emb, vs_matrix)
            top_distances = np.sort(distances)[:N].tolist()  # Top N sorted distances
            top_indices = np.argsort(distances)[:N]  # Indices of top N distances
            top_texts = [vector_store.loc[idx, "text"] for idx in top_indices]

            ensemble.append([top_distances, top_indices.tolist(), top_texts])

        ordered_ensemble = []

        for k in range(len(ensemble)):
            sort_indices = np.argsort(
                ensemble[k][1],
            )  # Sort based on the indices in the second sublist
            ordered_ensemble.append(
                [
                    [ensemble[k][e][i] for i in sort_indices]
                    for e in range(3)  # Reorder each sublist
                ],
            )

        return ensemble, ordered_ensemble

    def process_prompt(self, prompt):
        table = self.bq_client.list_rows(
            self.bq_client.get_table(self.table_name),
        ).to_dataframe()
        distance_metric = "euclidean"
        prompt = input("Prompt> ")

        _, ordered_ensemble = self.homemade_vector_search(
            prompt=prompt,
            vector_store=table,
            embedding_model=self.embedding_model,
            distance_metric=distance_metric,
        )

        context = " ".join(ordered_ensemble[0][2])

        prompt = f"""
        Context: {context}
        Prompt: {prompt}
        """

        self.vx_model.generate_message_information(self.chat, prompt)
