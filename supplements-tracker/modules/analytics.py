"""
Модуль для аналитики и визуализации данных о приеме БАДов
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats


class SupplementAnalytics:
    """Класс для анализа данных о приеме БАДов"""

    def __init__(self, df_intake: pd.DataFrame, df_labs: pd.DataFrame):
        """
        Инициализация аналитики

        Args:
            df_intake: DataFrame с данными о ежедневном приеме
            df_labs: DataFrame с результатами анализов
        """
        self.df_intake = df_intake.copy()
        self.df_labs = df_labs.copy()

        # Преобразуем даты
        if not self.df_intake.empty:
            self.df_intake['date'] = pd.to_datetime(self.df_intake['date'])

        if not self.df_labs.empty:
            self.df_labs['date'] = pd.to_datetime(self.df_labs['date'])

    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Расчет основной статистики

        Returns:
            Словарь со статистикой
        """
        if self.df_intake.empty:
            return {}

        total_days = len(self.df_intake)
        omega3_days = self.df_intake['omega3_taken'].sum()
        d3_days = self.df_intake['d3_taken'].sum()

        stats = {
            'total_days': total_days,
            'omega3_compliance': (omega3_days / total_days * 100) if total_days > 0 else 0,
            'd3_compliance': (d3_days / total_days * 100) if total_days > 0 else 0,
            'avg_energy': self.df_intake['energy_level'].mean(),
            'avg_sleep': self.df_intake['sleep_quality'].mean(),
            'avg_mood': self.df_intake['mood_level'].mean(),
            'avg_omega3_dose': self.df_intake[self.df_intake['omega3_taken'] == 1]['omega3_dose'].mean(),
            'avg_d3_dose': self.df_intake[self.df_intake['d3_taken'] == 1]['d3_dose'].mean(),
        }

        # Добавляем информацию о последнем анализе
        if not self.df_labs.empty:
            last_lab = self.df_labs.iloc[-1]
            stats['last_vitamin_d'] = last_lab['vitamin_d_level']
            stats['last_omega3_index'] = last_lab['omega3_index']
            stats['last_lab_date'] = last_lab['date'].strftime('%Y-%m-%d')

        return stats

    def plot_vitamin_d_trend(self, target_min: float = 50, target_max: float = 80) -> go.Figure:
        """
        График динамики уровня витамина D

        Args:
            target_min: Минимальное целевое значение
            target_max: Максимальное целевое значение

        Returns:
            Plotly Figure
        """
        if self.df_labs.empty or self.df_labs['vitamin_d_level'].isna().all():
            # Возвращаем пустой график с сообщением
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных о витамине D",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            fig.update_layout(title="Динамика уровня витамина D")
            return fig

        df_vit_d = self.df_labs[self.df_labs['vitamin_d_level'].notna()].copy()

        fig = go.Figure()

        # График уровня витамина D
        fig.add_trace(go.Scatter(
            x=df_vit_d['date'],
            y=df_vit_d['vitamin_d_level'],
            mode='lines+markers',
            name='Уровень витамина D',
            line=dict(color='orange', width=3),
            marker=dict(size=10)
        ))

        # Целевая зона
        fig.add_hrect(
            y0=target_min, y1=target_max,
            fillcolor="green", opacity=0.1,
            layer="below", line_width=0,
            annotation_text="Целевая зона",
            annotation_position="top left"
        )

        # Линии целевых значений
        fig.add_hline(y=target_min, line_dash="dash", line_color="green",
                     annotation_text=f"Мин: {target_min} нг/мл")
        fig.add_hline(y=target_max, line_dash="dash", line_color="green",
                     annotation_text=f"Макс: {target_max} нг/мл")

        fig.update_layout(
            title="Динамика уровня витамина D (25-OH)",
            xaxis_title="Дата анализа",
            yaxis_title="Уровень витамина D (нг/мл)",
            hovermode='x unified',
            height=500
        )

        return fig

    def plot_omega3_index(self, target_min: float = 8.0) -> go.Figure:
        """
        График омега-3 индекса

        Args:
            target_min: Минимальное целевое значение

        Returns:
            Plotly Figure
        """
        if self.df_labs.empty or self.df_labs['omega3_index'].isna().all():
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных об омега-3 индексе",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            fig.update_layout(title="Динамика омега-3 индекса")
            return fig

        df_omega = self.df_labs[self.df_labs['omega3_index'].notna()].copy()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_omega['date'],
            y=df_omega['omega3_index'],
            mode='lines+markers',
            name='Омега-3 индекс',
            line=dict(color='blue', width=3),
            marker=dict(size=10)
        ))

        # Целевая линия
        fig.add_hline(y=target_min, line_dash="dash", line_color="green",
                     annotation_text=f"Целевое значение: {target_min}%")

        fig.update_layout(
            title="Динамика омега-3 индекса",
            xaxis_title="Дата анализа",
            yaxis_title="Омега-3 индекс (%)",
            hovermode='x unified',
            height=500
        )

        return fig

    def plot_intake_calendar(self, supplement: str = 'omega3') -> go.Figure:
        """
        Календарь приема БАДов (тепловая карта)

        Args:
            supplement: Тип БАДа ('omega3' или 'd3')

        Returns:
            Plotly Figure
        """
        if self.df_intake.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных о приеме",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            return fig

        df = self.df_intake.copy()
        df['week'] = df['date'].dt.isocalendar().week
        df['day_of_week'] = df['date'].dt.dayofweek
        df['year'] = df['date'].dt.year

        column = f'{supplement}_taken'
        title = 'Омега-3' if supplement == 'omega3' else 'Витамин D3'

        # Создаем pivot table для heatmap
        pivot = df.pivot_table(
            values=column,
            index='day_of_week',
            columns='week',
            aggfunc='mean'
        )

        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=days,
            colorscale='RdYlGn',
            text=pivot.values,
            texttemplate='%{text:.0f}',
            textfont={"size": 10},
            colorbar=dict(title="Прием")
        ))

        fig.update_layout(
            title=f"Календарь приема {title}",
            xaxis_title="Неделя года",
            yaxis_title="День недели",
            height=400
        )

        return fig

    def calculate_correlation(self) -> pd.DataFrame:
        """
        Расчет корреляции между приемом БАДов и самочувствием

        Returns:
            DataFrame с корреляциями
        """
        if self.df_intake.empty:
            return pd.DataFrame()

        # Выбираем только числовые колонки для корреляции
        numeric_cols = ['omega3_taken', 'd3_taken', 'energy_level', 'sleep_quality', 'mood_level']
        df_numeric = self.df_intake[numeric_cols].dropna()

        if df_numeric.empty:
            return pd.DataFrame()

        corr_matrix = df_numeric.corr()

        return corr_matrix

    def plot_correlation_heatmap(self) -> go.Figure:
        """
        Тепловая карта корреляций

        Returns:
            Plotly Figure
        """
        corr = self.calculate_correlation()

        if corr.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Недостаточно данных для расчета корреляций",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            return fig

        labels = {
            'omega3_taken': 'Омега-3',
            'd3_taken': 'Витамин D3',
            'energy_level': 'Энергия',
            'sleep_quality': 'Сон',
            'mood_level': 'Настроение'
        }

        renamed_corr = corr.rename(index=labels, columns=labels)

        fig = go.Figure(data=go.Heatmap(
            z=renamed_corr.values,
            x=list(renamed_corr.columns),
            y=list(renamed_corr.index),
            colorscale='RdBu',
            zmid=0,
            text=renamed_corr.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Корреляция")
        ))

        fig.update_layout(
            title="Корреляция между приемом БАДов и самочувствием",
            height=500,
            width=600
        )

        return fig

    def plot_wellbeing_trends(self) -> go.Figure:
        """
        График трендов самочувствия

        Returns:
            Plotly Figure
        """
        if self.df_intake.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Нет данных о самочувствии",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            return fig

        df = self.df_intake.copy()

        fig = go.Figure()

        # График энергии
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['energy_level'],
            mode='lines+markers',
            name='Энергия',
            line=dict(color='red')
        ))

        # График сна
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['sleep_quality'],
            mode='lines+markers',
            name='Качество сна',
            line=dict(color='blue')
        ))

        # График настроения
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['mood_level'],
            mode='lines+markers',
            name='Настроение',
            line=dict(color='green')
        ))

        fig.update_layout(
            title="Динамика показателей самочувствия",
            xaxis_title="Дата",
            yaxis_title="Оценка (1-10)",
            hovermode='x unified',
            height=500
        )

        return fig

    def predict_target_achievement(self, current_level: float, target_level: float,
                                   daily_dose: float, absorption_rate: float = 100) -> Dict[str, Any]:
        """
        Прогноз достижения целевого уровня витамина D

        Args:
            current_level: Текущий уровень (нг/мл)
            target_level: Целевой уровень (нг/мл)
            daily_dose: Ежедневная доза (МЕ)
            absorption_rate: Процент усвоения (по умолчанию 100)

        Returns:
            Словарь с прогнозом
        """
        # Упрощенная модель: 100 МЕ витамина D повышают уровень на ~1 нг/мл
        # при ежедневном приеме в течение 2-3 месяцев
        daily_increase = (daily_dose / 100) * (absorption_rate / 100) / 60  # на день

        if daily_increase <= 0:
            return {
                'days_to_target': None,
                'weeks_to_target': None,
                'achievable': False,
                'message': 'Дозировка недостаточна для достижения цели'
            }

        level_diff = target_level - current_level

        if level_diff <= 0:
            return {
                'days_to_target': 0,
                'weeks_to_target': 0,
                'achievable': True,
                'message': 'Целевой уровень уже достигнут'
            }

        days_to_target = int(level_diff / daily_increase)
        weeks_to_target = days_to_target / 7

        return {
            'days_to_target': days_to_target,
            'weeks_to_target': round(weeks_to_target, 1),
            'achievable': True,
            'message': f'Прогноз: целевой уровень будет достигнут через {days_to_target} дней ({weeks_to_target:.1f} недель)'
        }

    def export_summary_report(self) -> str:
        """
        Создание текстового отчета со статистикой

        Returns:
            Текст отчета
        """
        stats = self.calculate_statistics()

        report = f"""
╔═══════════════════════════════════════════════════════════╗
║        ОТЧЕТ О ПРИЕМЕ БАДов - {datetime.now().strftime('%Y-%m-%d')}       ║
╚═══════════════════════════════════════════════════════════╝

ОБЩАЯ СТАТИСТИКА
────────────────────────────────────────────────────────────
Всего дней отслеживания: {stats.get('total_days', 0)}
Соблюдение приема Омега-3: {stats.get('omega3_compliance', 0):.1f}%
Соблюдение приема Витамина D3: {stats.get('d3_compliance', 0):.1f}%

СРЕДНИЕ ПОКАЗАТЕЛИ САМОЧУВСТВИЯ
────────────────────────────────────────────────────────────
Уровень энергии: {stats.get('avg_energy', 0):.1f}/10
Качество сна: {stats.get('avg_sleep', 0):.1f}/10
Настроение: {stats.get('avg_mood', 0):.1f}/10

ДОЗИРОВКИ
────────────────────────────────────────────────────────────
Средняя доза Омега-3: {stats.get('avg_omega3_dose', 0):.0f} мг EPA+DHA
Средняя доза Витамина D3: {stats.get('avg_d3_dose', 0):.0f} МЕ

ПОСЛЕДНИЕ АНАЛИЗЫ
────────────────────────────────────────────────────────────
"""

        if 'last_lab_date' in stats:
            report += f"Дата: {stats['last_lab_date']}\n"
            if stats.get('last_vitamin_d'):
                report += f"Витамин D (25-OH): {stats['last_vitamin_d']:.1f} нг/мл\n"
            if stats.get('last_omega3_index'):
                report += f"Омега-3 индекс: {stats['last_omega3_index']:.1f}%\n"
        else:
            report += "Анализы еще не проводились\n"

        report += "\n═══════════════════════════════════════════════════════════\n"

        return report
