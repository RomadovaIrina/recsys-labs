import streamlit as st
from service.exceptions import ApiError
from io import BytesIO
from PIL import Image


def process_api(api_name, image, api1, api2):
    # Получаем байты изображения
    image_bytes = image.getvalue()
    img = Image.open(BytesIO(image_bytes))

    # Сохраняем изображение в файл временно
    img_path = "temp_image.png"
    img.save(img_path)

    try:
        if api_name == "API_1":
            result = api1.recognize_logo(img_path)
        elif api_name == "API_2":
            result = api2.detect_logo(img_path)
    except ApiError as e:
        return {"error": f"{e.message}", "status": e.status_code}

    return result


def render_single_api_result(api_name, image, result):
    if "error" in result:
        st.error(result)
        return

    st.image(image, caption="Загруженное изображение", width="stretch")
    st.subheader(f"Результат работы {api_name}:")

    if api_name == "API_1":
        st.write(result)
    elif api_name == "API_2":
        st.write(result)


def render_comparison_result(image, api1, api2):
    with st.spinner("Обрабатываем изображение через оба API..."):
        result1 = process_api("API_1", image, api1, api2)
        result2 = process_api("API_2", image, api1, api2)

    st.image(image, caption="Загруженное изображение", width="stretch")

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.subheader("Результат работы API_1:")
        if "error" in result1:
            st.error(result1)
        else:
            st.json(result1)

    with col_res2:
        st.subheader("Результат работы API_2:")
        if "error" in result2:
            st.error(result2)
        else:
            st.json(result2)


def api_detector(api1, api2):
    st.set_page_config(page_title="Logo Detect Comparison", layout="wide")

    cent_col = st.columns([1, 2, 1])[1]

    uploaded_image = cent_col.file_uploader(
        "Загрузите изображение с логотипом",
        type=["png", "jpg", "jpeg"])
    button_col = cent_col.columns([1, 1, 1])[1]
    api_choice = button_col.radio(label="Выберите API",
                                  options=["API_1", "API_2", "Сравнение API"])
    buttons_col = cent_col.columns([1, 1, 1])[1]
    clicked = buttons_col.button("Детектировать логотип")

    if clicked and uploaded_image is not None:
        with cent_col:
            if api_choice in ["API_1", "API_2"]:
                result = process_api(api_choice, uploaded_image, api1, api2)
                render_single_api_result(api_choice, uploaded_image, result)
            elif api_choice == "Сравнение API":
                render_comparison_result(uploaded_image, api1, api2)
