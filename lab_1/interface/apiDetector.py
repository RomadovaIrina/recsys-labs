import streamlit as st
from service.exceptions import ApiError
from io import BytesIO
from PIL import Image
from typing import Dict, Any

# Функция для расположения ответа от одного апи на страничке
def place_one_res(api_name: str, image: Image.Image, api1, api2) -> None:
    image_bytes = image.getvalue()
    image_file = BytesIO(image_bytes)
    try:
        if api_name == "API_1":
            result: Dict[str, Any] = api1.recognize_logo(image_file)
            st.image(image, caption="Загруженное изображение", width="stretch")
            st.subheader(f"Результат работы {api_name}:")
            st.json(result)
            return

        elif api_name == "API_2":
            result, boxed_img = api2.detect_logo(image_file)
            st.image(image, caption="Загруженное изображение", width="stretch")
            st.subheader(f"Результат работы {api_name}:")
            st.json(result)
            if boxed_img:
                st.image(boxed_img, caption="Изображение с ббоксами", width="stretch")

    except ApiError as e:
        st.error(f"Статус: {e.status_code}")
        return


# Функция для расположения ответов от обоих апи на странице
def place_both_res(image: Image.Image, api1, api2) -> None:
    with st.spinner("Обрабатываем изображение через оба API..."):
        image_bytes = image.getvalue()
        image_file = BytesIO(image_bytes)
        result1 = None
        try:
            result1: Dict[str, Any] = api1.recognize_logo(image_file)
        except ApiError as e:
            result1 = {"error": f"{e.message}, Статус: {e.status_code}"}
        try:
            result2, image_with_bbox2 = api2.detect_logo(image_file)
        except ApiError as e:
            result2 = {"error": f"{e.message}, Статус: {e.status_code}"}

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
            if image_with_bbox2:
                st.image(
                    image_with_bbox2,
                    caption="Изображение с ббоксами",
                    use_column_width=True,
                )


# Основная функция интерфейса где настроена страница
def logo_detect_gui(api1, api2) -> None:
    st.set_page_config(page_title="Logo Detect Comparison", layout="wide")

    cent_col = st.columns([1, 2, 1])[1]

    uploaded_image = cent_col.file_uploader(
        "Загрузите изображение", type=["png", "jpg", "jpeg"]
    )
    button_col = cent_col.columns([1, 1, 1])[1]
    api_choice = button_col.radio(
        label="Выберите API", options=["API_1", "API_2", "Сравнение API"]
    )
    buttons_col = cent_col.columns([1, 1, 1])[1]
    clicked = buttons_col.button("Обработать")

    if clicked and uploaded_image is not None:
        with cent_col:
            if api_choice in ["API_1", "API_2"]:
                place_one_res(api_choice, uploaded_image, api1, api2)
            elif api_choice == "Сравнение API":
                place_both_res(uploaded_image, api1, api2)
