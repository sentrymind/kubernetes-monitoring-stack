"""
Главное приложение Streamlit для отслеживания приема БАДов
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import SupplementsDB
from modules.analytics import SupplementAnalytics
from modules.pdf_export import PDFReportGenerator

# Настройка страницы
st.set_page_config(
    page_title="Трекер БАДов",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация базы данных
@st.cache_resource
def init_database():
    """Инициализация базы данных"""
    return SupplementsDB("data/supplements.db")

db = init_database()

# Заголовок приложения
st.title("💊 Трекер приема БАДов")
st.markdown("---")

# Боковая панель
with st.sidebar:
    st.header("Навигация")
    page = st.radio(
        "Выберите раздел:",
        ["Дашборд", "Добавить запись", "Анализы", "Стоимость", "Импорт/Экспорт", "Отчеты"]
    )

    st.markdown("---")
    st.info("""
    **О приложении:**

    Трекер для отслеживания приема БАДов
    (Омега-3, Витамин D3-K2) с визуализацией
    результатов и аналитикой.
    """)

# ===== СТРАНИЦА: ДАШБОРД =====
if page == "Дашборд":
    st.header("📊 Дашборд")

    # Получаем данные
    df_intake = db.get_daily_intake()
    df_labs = db.get_lab_results()

    if df_intake.empty:
        st.warning("Нет данных для отображения. Добавьте первую запись!")
    else:
        # Создаем аналитику
        analytics = SupplementAnalytics(df_intake, df_labs)
        stats = analytics.calculate_statistics()

        # Метрики
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Дней отслеживания",
                stats.get('total_days', 0)
            )

        with col2:
            st.metric(
                "Соблюдение Омега-3",
                f"{stats.get('omega3_compliance', 0):.1f}%"
            )

        with col3:
            st.metric(
                "Соблюдение D3",
                f"{stats.get('d3_compliance', 0):.1f}%"
            )

        with col4:
            if 'last_vitamin_d' in stats:
                st.metric(
                    "Витамин D",
                    f"{stats.get('last_vitamin_d', 0):.1f} нг/мл"
                )
            else:
                st.metric("Витамин D", "N/A")

        st.markdown("---")

        # Показатели самочувствия
        st.subheader("🎯 Средние показатели самочувствия")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Энергия", f"{stats.get('avg_energy', 0):.1f}/10")

        with col2:
            st.metric("Качество сна", f"{stats.get('avg_sleep', 0):.1f}/10")

        with col3:
            st.metric("Настроение", f"{stats.get('avg_mood', 0):.1f}/10")

        st.markdown("---")

        # Графики
        st.subheader("📈 Графики и визуализация")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Витамин D", "Омега-3", "Календарь приема", "Самочувствие"]
        )

        with tab1:
            st.plotly_chart(
                analytics.plot_vitamin_d_trend(),
                use_container_width=True
            )

        with tab2:
            st.plotly_chart(
                analytics.plot_omega3_index(),
                use_container_width=True
            )

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    analytics.plot_intake_calendar('omega3'),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    analytics.plot_intake_calendar('d3'),
                    use_container_width=True
                )

        with tab4:
            st.plotly_chart(
                analytics.plot_wellbeing_trends(),
                use_container_width=True
            )

        # Корреляции
        st.markdown("---")
        st.subheader("🔗 Корреляция между приемом и самочувствием")
        st.plotly_chart(
            analytics.plot_correlation_heatmap(),
            use_container_width=True
        )

        # Напоминание о следующем анализе
        next_test_date = db.get_next_lab_test_date()
        if next_test_date:
            next_date = datetime.strptime(next_test_date, '%Y-%m-%d')
            days_until = (next_date - datetime.now()).days

            if days_until <= 7:
                st.warning(f"⚠️ Следующий анализ рекомендуется сдать {next_test_date} (через {days_until} дней)")
            elif days_until <= 30:
                st.info(f"ℹ️ Следующий анализ рекомендуется сдать {next_test_date} (через {days_until} дней)")

# ===== СТРАНИЦА: ДОБАВИТЬ ЗАПИСЬ =====
elif page == "Добавить запись":
    st.header("➕ Добавить ежедневную запись")

    with st.form("daily_intake_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Дата", datetime.now())

            st.subheader("Омега-3")
            omega3_taken = st.checkbox("Принято")
            omega3_dose = st.number_input("Доза EPA+DHA (мг)", min_value=0, value=1000, step=100)

            st.subheader("Витамин D3")
            d3_taken = st.checkbox("Принято", key="d3_taken")
            d3_dose = st.number_input("Доза (МЕ)", min_value=0, value=5000, step=1000)

            st.subheader("Витамин K2 (опционально)")
            k2_taken = st.checkbox("Принято", key="k2_taken")
            k2_dose = st.number_input("Доза (мкг)", min_value=0, value=200, step=50)

        with col2:
            st.subheader("Самочувствие")

            energy = st.slider("Уровень энергии", 1, 10, 5)
            sleep = st.slider("Качество сна", 1, 10, 5)
            mood = st.slider("Настроение", 1, 10, 5)

            notes = st.text_area("Заметки (опционально)")

        submitted = st.form_submit_button("Сохранить запись")

        if submitted:
            data = {
                'date': date.strftime('%Y-%m-%d'),
                'omega3_dose': omega3_dose if omega3_taken else None,
                'omega3_taken': 1 if omega3_taken else 0,
                'd3_dose': d3_dose if d3_taken else None,
                'd3_taken': 1 if d3_taken else 0,
                'k2_dose': k2_dose if k2_taken else None,
                'k2_taken': 1 if k2_taken else 0,
                'energy_level': energy,
                'sleep_quality': sleep,
                'mood_level': mood,
                'notes': notes
            }

            if db.add_daily_intake(data):
                st.success("✅ Запись успешно добавлена!")
                st.balloons()
            else:
                st.error("❌ Ошибка при добавлении записи")

# ===== СТРАНИЦА: АНАЛИЗЫ =====
elif page == "Анализы":
    st.header("🔬 Результаты анализов")

    # Форма добавления результатов
    with st.expander("➕ Добавить результаты анализов"):
        with st.form("lab_results_form"):
            lab_date = st.date_input("Дата анализа", datetime.now())

            col1, col2 = st.columns(2)

            with col1:
                vit_d = st.number_input("Уровень витамина D 25(OH) (нг/мл)", min_value=0.0, value=50.0, step=0.1)

            with col2:
                omega3_idx = st.number_input("Омега-3 индекс (%)", min_value=0.0, value=8.0, step=0.1)

            lab_notes = st.text_area("Заметки")

            submitted = st.form_submit_button("Сохранить результаты")

            if submitted:
                data = {
                    'date': lab_date.strftime('%Y-%m-%d'),
                    'vitamin_d_level': vit_d,
                    'omega3_index': omega3_idx,
                    'notes': lab_notes
                }

                if db.add_lab_result(data):
                    st.success("✅ Результаты анализов добавлены!")
                else:
                    st.error("❌ Ошибка при добавлении результатов")

    # Показываем историю анализов
    st.markdown("---")
    st.subheader("📋 История анализов")

    df_labs = db.get_lab_results()

    if df_labs.empty:
        st.info("Нет результатов анализов. Добавьте первый результат!")
    else:
        # Форматируем DataFrame для отображения
        display_df = df_labs[['date', 'vitamin_d_level', 'omega3_index', 'notes']].copy()
        display_df.columns = ['Дата', 'Витамин D (нг/мл)', 'Омега-3 индекс (%)', 'Заметки']

        st.dataframe(display_df, use_container_width=True)

        # Прогноз достижения цели
        st.markdown("---")
        st.subheader("🎯 Прогноз достижения целевого уровня витамина D")

        col1, col2, col3 = st.columns(3)

        with col1:
            current_level = st.number_input(
                "Текущий уровень (нг/мл)",
                value=float(df_labs.iloc[-1]['vitamin_d_level']) if not df_labs.empty else 30.0
            )

        with col2:
            target_level = st.number_input("Целевой уровень (нг/мл)", value=60.0)

        with col3:
            daily_dose = st.number_input("Ежедневная доза (МЕ)", value=5000)

        if st.button("Рассчитать прогноз"):
            analytics = SupplementAnalytics(db.get_daily_intake(), df_labs)
            prediction = analytics.predict_target_achievement(
                current_level, target_level, daily_dose
            )

            if prediction['achievable']:
                if prediction['days_to_target'] == 0:
                    st.success(prediction['message'])
                else:
                    st.info(f"📅 {prediction['message']}")
            else:
                st.warning(prediction['message'])

# ===== СТРАНИЦА: СТОИМОСТЬ =====
elif page == "Стоимость":
    st.header("💰 Учет стоимости БАДов")

    # Форма добавления
    with st.expander("➕ Добавить покупку"):
        with st.form("cost_form"):
            col1, col2 = st.columns(2)

            with col1:
                supplement_name = st.text_input("Название БАДа")
                purchase_date = st.date_input("Дата покупки", datetime.now())
                cost = st.number_input("Стоимость (руб)", min_value=0.0, value=1000.0, step=100.0)

            with col2:
                quantity = st.number_input("Количество (капсул/таблеток)", min_value=1, value=60)
                dose_per_unit = st.number_input("Доза на единицу", min_value=0.0, value=1000.0)
                cost_notes = st.text_area("Заметки")

            submitted = st.form_submit_button("Сохранить")

            if submitted:
                if not supplement_name:
                    st.error("Укажите название БАДа")
                else:
                    data = {
                        'supplement_name': supplement_name,
                        'purchase_date': purchase_date.strftime('%Y-%m-%d'),
                        'cost': cost,
                        'quantity': quantity,
                        'dose_per_unit': dose_per_unit,
                        'notes': cost_notes
                    }

                    if db.add_supplement_cost(data):
                        st.success("✅ Информация о покупке сохранена!")
                    else:
                        st.error("❌ Ошибка при сохранении")

    # История покупок
    st.markdown("---")
    st.subheader("📊 История покупок")

    # Фильтр по периоду
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("С даты", datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("По дату", datetime.now())

    df_costs = db.get_supplement_costs(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    if df_costs.empty:
        st.info("Нет данных о покупках за выбранный период")
    else:
        # Показываем таблицу
        display_df = df_costs[['purchase_date', 'supplement_name', 'cost', 'quantity', 'dose_per_unit']].copy()
        display_df.columns = ['Дата', 'Название', 'Стоимость (руб)', 'Количество', 'Доза/единицу']

        st.dataframe(display_df, use_container_width=True)

        # Общая статистика
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Всего покупок", len(df_costs))

        with col2:
            total_cost = df_costs['cost'].sum()
            st.metric("Общие расходы", f"{total_cost:.0f} руб")

        with col3:
            avg_cost = df_costs['cost'].mean()
            st.metric("Средняя покупка", f"{avg_cost:.0f} руб")

# ===== СТРАНИЦА: ИМПОРТ/ЭКСПОРТ =====
elif page == "Импорт/Экспорт":
    st.header("📁 Импорт и экспорт данных")

    tab1, tab2 = st.tabs(["Импорт", "Экспорт"])

    with tab1:
        st.subheader("Импорт из CSV")

        table_name = st.selectbox(
            "Выберите таблицу для импорта:",
            ["daily_intake", "lab_results", "supplement_costs"]
        )

        uploaded_file = st.file_uploader("Выберите CSV файл", type=['csv'])

        if uploaded_file is not None:
            # Показываем превью
            df_preview = pd.read_csv(uploaded_file)
            st.write("Превью данных:")
            st.dataframe(df_preview.head())

            if st.button("Импортировать данные"):
                # Сохраняем файл временно
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())

                if db.import_from_csv(temp_path, table_name):
                    st.success("✅ Данные успешно импортированы!")
                    os.remove(temp_path)
                else:
                    st.error("❌ Ошибка при импорте данных")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

    with tab2:
        st.subheader("Экспорт в CSV")

        export_table = st.selectbox(
            "Выберите таблицу для экспорта:",
            ["daily_intake", "lab_results", "supplement_costs"],
            key="export_table"
        )

        if st.button("Экспортировать"):
            output_path = f"export_{export_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            if db.export_to_csv(export_table, output_path):
                st.success(f"✅ Данные экспортированы в {output_path}")

                # Предлагаем скачать файл
                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="Скачать CSV",
                        data=f,
                        file_name=output_path,
                        mime='text/csv'
                    )
            else:
                st.error("❌ Ошибка при экспорте данных")

# ===== СТРАНИЦА: ОТЧЕТЫ =====
elif page == "Отчеты":
    st.header("📄 Генерация отчетов")

    df_intake = db.get_daily_intake()
    df_labs = db.get_lab_results()

    if df_intake.empty:
        st.warning("Нет данных для генерации отчета")
    else:
        analytics = SupplementAnalytics(df_intake, df_labs)
        stats = analytics.calculate_statistics()

        # Текстовый отчет
        st.subheader("📝 Текстовый отчет")

        report_text = analytics.export_summary_report()
        st.code(report_text, language=None)

        # Кнопка для копирования
        if st.button("Копировать отчет"):
            st.write("Скопируйте текст выше")

        st.markdown("---")

        # PDF отчет
        st.subheader("📑 PDF отчет")

        if st.button("Сгенерировать PDF отчет"):
            pdf_gen = PDFReportGenerator()

            try:
                pdf_path = pdf_gen.create_report(stats, analytics)
                st.success(f"✅ PDF отчет создан: {pdf_path}")

                # Предлагаем скачать
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="Скачать PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime='application/pdf'
                    )
            except Exception as e:
                st.error(f"❌ Ошибка при создании PDF: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Трекер приема БАДов v1.0 | Создано с помощью Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)
