from app.bot_ai.bot_multi_model import VertexAImultimodel


def start_onboarding():
    vx_model = VertexAImultimodel()
    chat, model = vx_model.start_chat()
    history = chat.history

    if len(history) == 0:
        name = input("¿Cuál es tu nombre y apellido?: ")
        response, history = vx_model.onboarding_process(
            onboarding_status="name",
            history=history,
            prompt=name,
        )

        response, history = vx_model.name_check(response, history)

        date = input("¿Cuál es tu fecha de nacimiento?: ")
        response, history = vx_model.onboarding_process(
            onboarding_status="date",
            history=history,
            prompt=date,
        )

        city = input("¿En qué ciudad vives?: ")
        response, history = vx_model.onboarding_process(
            onboarding_status="city",
            history=history,
            prompt=city,
        )
