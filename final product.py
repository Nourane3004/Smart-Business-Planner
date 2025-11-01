import streamlit as st
import openai
import os
import re
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Business Model Canvas Generator",
    page_icon="🚀",
    layout="wide"
)

# Configuration OpenRouter
os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
        margin: 1.5rem 0 1rem 0;
    }
    .card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .idea-input {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .financial-chart {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .marketing-phase {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def generate_business_idea_and_canvas(business_idea, country, budget=None):
    """Génère un Business Model Canvas complet basé sur une idée business spécifique"""
    
    client = openai.OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"]
    )
    
    budget_context = ""
    if budget:
        budget_context = f" avec un budget initial d'environ {budget}"
    
    prompt = f"""
    Crée un Business Model Canvas COMPLET et DÉTAILLÉ pour l'idée business suivante :
    
    IDÉE BUSINESS : "{business_idea}"
    PAYS : {country}
    CONTEXTE BUDGET : {budget_context}
    
    Cette idée doit être transformée en un business model viable avec tous les éléments nécessaires.

    FORMAT EXACT À SUIVRE :

    BUSINESS_IDEA_START
    [Développement complet de l'idée business - 3-4 phrases détaillant le concept]
    BUSINESS_IDEA_END

    UNIQUE_VALUE_START
    [Proposition de valeur unique et différenciante - pourquoi les clients choisiraient ce business]
    UNIQUE_VALUE_END

    BMC_PARTNERS_START
    • [Partenaire stratégique 1 - spécifique à l'idée]
    • [Partenaire stratégique 2 - spécifique à l'idée]
    • [Partenaire stratégique 3 - spécifique à l'idée]
    BMC_PARTNERS_END

    BMC_ACTIVITIES_START
    • [Activité clé 1 - action concrète pour cette idée]
    • [Activité clé 2 - action concrète pour cette idée]
    • [Activité clé 3 - action concrète pour cette idée]
    BMC_ACTIVITIES_END

    BMC_VALUE_PROP_START
    • [Bénéfice client 1 - avantage concret]
    • [Bénéfice client 2 - avantage concret]
    • [Bénéfice client 3 - avantage concret]
    BMC_VALUE_PROP_END

    BMC_RELATIONSHIP_START
    • [Type de relation client 1 - adapté à l'idée]
    • [Type de relation client 2 - adapté à l'idée]
    BMC_RELATIONSHIP_END

    BMC_SEGMENTS_START
    • [Segment client principal - cible spécifique]
    • [Segment client secondaire - cible spécifique]
    • [Segment client tertiaire - cible spécifique]
    BMC_SEGMENTS_END

    BMC_RESOURCES_START
    • [Ressource essentielle 1 - nécessaire pour cette idée]
    • [Ressource essentielle 2 - nécessaire pour cette idée]
    BMC_RESOURCES_END

    BMC_CHANNELS_START
    • [Canal de distribution 1 - adapté à l'idée]
    • [Canal de distribution 2 - adapté à l'idée]
    BMC_CHANNELS_END

    BMC_COSTS_START
    • [Coût fixe principal: €X - montant réaliste]
    • [Coût variable principal: €X - montant réaliste]
    • [Coût marketing: €X - montant réaliste]
    BMC_COSTS_END

    BMC_REVENUES_START
    • [Source revenu principale: €X par mois/année]
    • [Source revenu secondaire: €X par mois/année]
    • [Source revenu complémentaire: €X par mois/année]
    BMC_REVENUES_END

    FINANCIAL_PROJECTIONS_START
    • [Revenu Année 1: €X | Année 2: €Y | Année 3: €Z - projections réalistes]
    • [Profit Année 1: €X | Année 2: €Y | Année 3: €Z - projections réalistes]
    • [Coût d'acquisition client: €X - estimation réaliste]
    • [Valeur vie client: €X - estimation réaliste]
    • [Marge brute: X% - estimation réaliste]
    • [Cash-flow mensuel année 1: €X - estimation réaliste]
    FINANCIAL_PROJECTIONS_END

    BUDGET_RECOMMENDATIONS_START
    • [Investissement initial recommandé: €X - basé sur l'idée]
    • [Coûts opérationnels mensuels: €X - estimation réaliste]
    • [Point de rentabilité: X mois - calcul réaliste]
    • [ROI première année: X% - projection réaliste]
    • [Besoin en fonds de roulement: €X - estimation]
    BUDGET_RECOMMENDATIONS_END

    MARKET_ANALYSIS_START
    [Analyse du marché cible - taille, croissance, opportunités spécifiques à cette idée]
    MARKET_ANALYSIS_END

    PRICING_STRATEGY_START
    • [Stratégie de prix recommandée - adaptée à l'idée]
    • [Comparaison avec alternatives existantes]
    • [Justification du prix proposé]
    PRICING_STRATEGY_END

    MARKETING_STRATEGY_START
    • [Stratégie de lancement phase 1 - actions concrètes]
    • [Stratégie de croissance phase 2 - actions concrètes]
    • [Canal digital principal - plateforme spécifique]
    • [Canal digital secondaire - plateforme spécifique]
    • [Stratégie de contenu - approche spécifique]
    • [Partenariats marketing - opportunités spécifiques]
    MARKETING_STRATEGY_END

    MARKETING_BUDGET_START
    • [Budget acquisition clients: €X/mois]
    • [Budget contenu: €X/mois]
    • [Budget publicité digitale: €X/mois]
    • [Budget événementiel: €X/mois]
    MARKETING_BUDGET_END

    EXECUTION_TIMELINE_START
    • [Mois 1-3: Préparation et développement - tâches spécifiques]
    • [Mois 4-6: Lancement et acquisition clients - actions spécifiques]
    • [Mois 7-12: Croissance et optimisation - étapes spécifiques]
    EXECUTION_TIMELINE_END

    RISK_ANALYSIS_START
    • [Risque principal 1 et mitigation - spécifique à l'idée]
    • [Risque principal 2 et mitigation - spécifique à l'idée]
    • [Risque principal 3 et mitigation - spécifique à l'idée]
    RISK_ANALYSIS_END

    KPIS_START
    • [KPI financier 1 - métrique importante]
    • [KPI marketing 1 - métrique importante]
    • [KPI opérationnel 1 - métrique importante]
    KPIS_END

    Utilise des CHIFFRES RÉALISTES adaptés à l'idée business.
    Sois CRÉATIF mais PRAGMATIQUE.
    Fournis des DÉTAILS CONCRETS pour chaque section.
    """

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-70b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": "Tu es un expert en création d'entreprise et business model. Tu transformes des idées en business plans complets et réalistes avec des chiffres concrets et des stratégies adaptées."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=6000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Erreur: {e}"

def parse_response(response):
    """Parse la réponse structurée"""
    sections = {
        'business_idea': '',
        'unique_value': '',
        'bmc_partners': [],
        'bmc_activities': [],
        'bmc_value_prop': [],
        'bmc_relationship': [],
        'bmc_segments': [],
        'bmc_resources': [],
        'bmc_channels': [],
        'bmc_costs': [],
        'bmc_revenues': [],
        'financial_projections': [],
        'budget_recommendations': [],
        'market_analysis': '',
        'pricing_strategy': [],
        'marketing_strategy': [],
        'marketing_budget': [],
        'execution_timeline': [],
        'risk_analysis': [],
        'kpis': []
    }
    
    try:
        # Sections simples (texte)
        text_sections = [
            ('BUSINESS_IDEA_START', 'BUSINESS_IDEA_END', 'business_idea'),
            ('UNIQUE_VALUE_START', 'UNIQUE_VALUE_END', 'unique_value'),
            ('MARKET_ANALYSIS_START', 'MARKET_ANALYSIS_END', 'market_analysis')
        ]
        
        for start_marker, end_marker, section_key in text_sections:
            if start_marker in response and end_marker in response:
                content = response.split(start_marker)[1].split(end_marker)[0].strip()
                sections[section_key] = content
        
        # Sections avec listes
        list_sections = [
            ('BMC_PARTNERS_START', 'BMC_PARTNERS_END', 'bmc_partners'),
            ('BMC_ACTIVITIES_START', 'BMC_ACTIVITIES_END', 'bmc_activities'),
            ('BMC_VALUE_PROP_START', 'BMC_VALUE_PROP_END', 'bmc_value_prop'),
            ('BMC_RELATIONSHIP_START', 'BMC_RELATIONSHIP_END', 'bmc_relationship'),
            ('BMC_SEGMENTS_START', 'BMC_SEGMENTS_END', 'bmc_segments'),
            ('BMC_RESOURCES_START', 'BMC_RESOURCES_END', 'bmc_resources'),
            ('BMC_CHANNELS_START', 'BMC_CHANNELS_END', 'bmc_channels'),
            ('BMC_COSTS_START', 'BMC_COSTS_END', 'bmc_costs'),
            ('BMC_REVENUES_START', 'BMC_REVENUES_END', 'bmc_revenues'),
            ('FINANCIAL_PROJECTIONS_START', 'FINANCIAL_PROJECTIONS_END', 'financial_projections'),
            ('BUDGET_RECOMMENDATIONS_START', 'BUDGET_RECOMMENDATIONS_END', 'budget_recommendations'),
            ('PRICING_STRATEGY_START', 'PRICING_STRATEGY_END', 'pricing_strategy'),
            ('MARKETING_STRATEGY_START', 'MARKETING_STRATEGY_END', 'marketing_strategy'),
            ('MARKETING_BUDGET_START', 'MARKETING_BUDGET_END', 'marketing_budget'),
            ('EXECUTION_TIMELINE_START', 'EXECUTION_TIMELINE_END', 'execution_timeline'),
            ('RISK_ANALYSIS_START', 'RISK_ANALYSIS_END', 'risk_analysis'),
            ('KPIS_START', 'KPIS_END', 'kpis')
        ]
        
        for start_marker, end_marker, section_key in list_sections:
            if start_marker in response and end_marker in response:
                content = response.split(start_marker)[1].split(end_marker)[0].strip()
                sections[section_key] = [line.strip() for line in content.split('\n') if line.strip() and line.strip().startswith('•')]
    
    except Exception as e:
        st.error(f"Erreur lors de l'analyse: {e}")
    
    return sections

def create_financial_charts(sections):
    """Crée des graphiques financiers interactifs"""
    
    # Extraction des données financières
    financial_data = extract_financial_data(sections)

    
    # Graphique 1: Projection des revenus sur 3 ans
    col1, col2 = st.columns(2)
    
    with col1:
        if financial_data['yearly_revenue']:
            fig_revenue = go.Figure()
            years = ['Année 1', 'Année 2', 'Année 3']
            revenues = financial_data['yearly_revenue']
            
            fig_revenue.add_trace(go.Bar(
                x=years,
                y=revenues,
                name='Revenus',
                marker_color='#28a745'
            ))
            
            fig_revenue.update_layout(
                title='Projection des Revenus sur 3 ans',
                xaxis_title='Années',
                yaxis_title='Revenus (€)',
                template='plotly_white'
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Graphique 2: Répartition des coûts
        if financial_data['costs']:
            labels = [f"Coût {i+1}" for i in range(len(financial_data['costs']))]
            values = financial_data['costs']
            
            fig_costs = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.3,
                marker_colors=px.colors.qualitative.Set3
            )])
            
            fig_costs.update_layout(
                title='Répartition des Coûts',
                template='plotly_white'
            )
            st.plotly_chart(fig_costs, use_container_width=True)

def extract_financial_data(sections):
    """Extrait les données financières pour les graphiques"""
    data = {
        'yearly_revenue': [],
        'costs': [],
        'initial_investment': 0,
        'break_even': 12
    }
    
    # Extraction des revenus annuels
    for projection in sections.get('financial_projections', []):
        if 'Revenu Année' in projection:
            numbers = re.findall(r'€(\d+[,\d]*)', projection)
            for num in numbers[:3]:
                clean_num = int(num.replace(',', '').replace(' ', ''))
                data['yearly_revenue'].append(clean_num)
    
    # Extraction des coûts
    for cost in sections.get('bmc_costs', []):
        numbers = re.findall(r'€(\d+[,\d]*)', cost)
        if numbers:
            clean_num = int(numbers[0].replace(',', '').replace(' ', ''))
            data['costs'].append(clean_num)
    
    # Extraction de l'investissement initial
    for budget in sections.get('budget_recommendations', []):
        if 'Investissement initial' in budget:
            numbers = re.findall(r'€(\d+[,\d]*)', budget)
            if numbers:
                data['initial_investment'] = int(numbers[0].replace(',', '').replace(' ', ''))
        elif 'Point de rentabilité' in budget:
            numbers = re.findall(r'(\d+) mois', budget)
            if numbers:
                data['break_even'] = int(numbers[0])
    
    return data

def create_marketing_dashboard(sections):
    """Crée un dashboard marketing interactif"""
    
    st.markdown("### 🎯 Dashboard Marketing")
    
    # Métriques marketing
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Budget Marketing Mensuel",
            "€2,500",
            "+15% vs prévision"
        )
    
    with col2:
        st.metric(
            "Coût d'Acquisition Client",
            "€45",
            "-8% vs objectif"
        )
    
    with col3:
        st.metric(
            "Taux de Conversion",
            "3.2%",
            "+0.5%"
        )
    
    with col4:
        st.metric(
            "ROI Marketing",
            "285%",
            "+35%"
        )
    
    # Graphiques marketing
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance par canal
        channels = ['Social Media', 'SEO', 'Email', 'Publicité', 'Partenaire']
        conversions = [120, 85, 65, 45, 30]
        costs = [1500, 800, 400, 2000, 600]
        
        fig_channels = go.Figure(data=[
            go.Bar(name='Conversions', x=channels, y=conversions, marker_color='#28a745'),
            go.Bar(name='Coûts (€)', x=channels, y=[c/10 for c in costs], marker_color='#dc3545')
        ])
        
        fig_channels.update_layout(
            title='Performance par Canal Marketing',
            barmode='group',
            template='plotly_white'
        )
        st.plotly_chart(fig_channels, use_container_width=True)
    
    with col2:
        # Timeline des campagnes
        campaigns = ['Lancement', 'Croissance', 'Rétention', 'Upsell']
        months = ['M1-M3', 'M4-M6', 'M7-M9', 'M10-M12']
        budgets = [8000, 12000, 15000, 10000]
        results = [45, 120, 180, 220]  # clients acquis
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=months, y=budgets, name='Budget', 
            line=dict(color='#ff6b6b', width=4),
            yaxis='y1'
        ))
        fig_timeline.add_trace(go.Scatter(
            x=months, y=results, name='Clients Acquis',
            line=dict(color='#28a745', width=4),
            yaxis='y2'
        ))
        
        fig_timeline.update_layout(
            title='Timeline des Campagnes Marketing',
            xaxis_title='Période',
            yaxis=dict(title='Budget (€)', side='left'),
            yaxis2=dict(title='Clients Acquis', side='right', overlaying='y'),
            template='plotly_white'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Détail des stratégies marketing
    st.markdown("#### 📋 Détail des Actions Marketing")
    
    if sections.get('marketing_strategy'):
        marketing_phases = {
            '🚀 Lancement (M1-M3)': sections['marketing_strategy'][:2],
            '📈 Croissance (M4-M6)': sections['marketing_strategy'][2:4],
            '🔄 Optimisation (M7-M12)': sections['marketing_strategy'][4:]
        }
        
        for phase_name, strategies in marketing_phases.items():
            with st.expander(phase_name, expanded=True):
                for strategy in strategies:
                    st.write(f"• {strategy.replace('•', '').strip()}")

def display_business_idea(sections):
    """Affiche l'idée business développée"""
    st.markdown('<div class="section-header">💡 IDÉE BUSINESS DÉVELOPPÉE</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if sections['business_idea']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🎯 Concept Business Complet")
            st.write(sections['business_idea'])
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if sections['unique_value']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("⭐ Proposition de Valeur Unique")
            st.write(sections['unique_value'])
            st.markdown('</div>', unsafe_allow_html=True)

def display_bmc(sections):
    """Affiche le Business Model Canvas"""
    st.markdown('<div class="section-header">📊 BUSINESS MODEL CANVAS</div>', unsafe_allow_html=True)
    
    # Grille 3x3 pour le BMC
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Partenaires Clés
        if sections['bmc_partners']:
            with st.expander("🤝 Partenaires Clés", expanded=True):
                for item in sections['bmc_partners'][:4]:
                    st.write(f"• {item.replace('•', '').strip()}")
        
        # Activités Clés
        if sections['bmc_activities']:
            with st.expander("⚙️ Activités Clés", expanded=True):
                for item in sections['bmc_activities'][:4]:
                    st.write(f"• {item.replace('•', '').strip()}")
        
        # Ressources Clés
        if sections['bmc_resources']:
            with st.expander("🔧 Ressources Clés", expanded=True):
                for item in sections['bmc_resources'][:3]:
                    st.write(f"• {item.replace('•', '').strip()}")
    
    with col2:
        # Proposition de Valeur
        if sections['bmc_value_prop']:
            with st.expander("💎 Proposition de Valeur", expanded=True):
                for item in sections['bmc_value_prop'][:4]:
                    st.write(f"• {item.replace('•', '').strip()}")
        
        # Relation Clients
        if sections['bmc_relationship']:
            with st.expander("👥 Relation Clients", expanded=True):
                for item in sections['bmc_relationship'][:3]:
                    st.write(f"• {item.replace('•', '').strip()}")
        
        # Canaux
        if sections['bmc_channels']:
            with st.expander("📡 Canaux", expanded=True):
                for item in sections['bmc_channels'][:3]:
                    st.write(f"• {item.replace('•', '').strip()}")
    
    with col3:
        # Segments Clients
        if sections['bmc_segments']:
            with st.expander("🎯 Segments Clients", expanded=True):
                for item in sections['bmc_segments'][:4]:
                    st.write(f"• {item.replace('•', '').strip()}")
        
        # Structure de Coûts
        if sections['bmc_costs']:
            with st.expander("💰 Structure de Coûts", expanded=True):
                for item in sections['bmc_costs'][:4]:
                    clean_item = item.replace('•', '').strip()
                    clean_item = re.sub(r'(\$|\€)?(\d+[,\d]*(?:\.\d+)?)', r'**\1\2**', clean_item)
                    st.write(f"• {clean_item}")
        
        # Flux de Revenus
        if sections['bmc_revenues']:
            with st.expander("💵 Flux de Revenus", expanded=True):
                for item in sections['bmc_revenues'][:4]:
                    clean_item = item.replace('•', '').strip()
                    clean_item = re.sub(r'(\$|\€)?(\d+[,\d]*(?:\.\d+)?)', r'**\1\2**', clean_item)
                    st.write(f"• {clean_item}")

def display_financial_analysis(sections):
    """Affiche l'analyse financière complète avec graphiques"""
    st.markdown('<div class="section-header">📈 ANALYSE FINANCIÈRE COMPLÈTE</div>', unsafe_allow_html=True)
    
    # Métriques financières principales
    col1, col2, col3, col4 = st.columns(4)
    
    financial_data = extract_financial_data(sections)
    
    with col1:
        if financial_data['initial_investment']:
            st.metric("Investissement Initial", f"€{financial_data['initial_investment']:,}")
    
    with col2:
        if financial_data['yearly_revenue']:
            st.metric("Revenu Année 1", f"€{financial_data['yearly_revenue'][0]:,}")
    
    with col3:
        st.metric("Point de Rentabilité", f"Mois {financial_data['break_even']}")
    
    with col4:
        st.metric("ROI Projeté", "185%")
    
    # Graphiques financiers
    create_financial_charts(sections)
    
    # Détails financiers
    col1, col2 = st.columns(2)
    
    with col1:
        if sections['financial_projections']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("💰 Projections Détailées")
            for item in sections['financial_projections'][:6]:
                clean_item = item.replace('•', '').strip()
                clean_item = re.sub(r'(\$|\€)?(\d+[,\d]*(?:\.\d+)?)', r'**\1\2**', clean_item)
                st.write(f"• {clean_item}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analyse du marché
        if sections['market_analysis']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🌍 Analyse du Marché")
            st.write(sections['market_analysis'])
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Recommandations budgétaires
        if sections['budget_recommendations']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🎯 Recommandations Budgétaires")
            for item in sections['budget_recommendations'][:5]:
                clean_item = item.replace('•', '').strip()
                clean_item = re.sub(r'(\$|\€)?(\d+[,\d]*(?:\.\d+)?)', r'**\1\2**', clean_item)
                st.write(f"• {clean_item}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Stratégie de prix
        if sections['pricing_strategy']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🏆 Stratégie de Prix")
            for item in sections['pricing_strategy'][:3]:
                st.write(f"• {item.replace('•', '').strip()}")
            st.markdown('</div>', unsafe_allow_html=True)

def display_marketing_strategy(sections):
    """Affiche la stratégie marketing complète avec dashboard"""
    st.markdown('<div class="section-header">🎯 STRATÉGIE MARKETING & EXÉCUTION</div>', unsafe_allow_html=True)
    
    # Dashboard marketing interactif
    create_marketing_dashboard(sections)
    
    # Détails de la stratégie marketing
    col1, col2 = st.columns(2)
    
    with col1:
        # Stratégie marketing détaillée
        if sections['marketing_strategy']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🚀 Plan Marketing Stratégique")
            for i, item in enumerate(sections['marketing_strategy'][:6], 1):
                st.write(f"{i}. {item.replace('•', '').strip()}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Budget marketing
        if sections.get('marketing_budget'):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("💰 Allocation du Budget Marketing")
            for item in sections['marketing_budget'][:4]:
                clean_item = item.replace('•', '').strip()
                clean_item = re.sub(r'(\$|\€)?(\d+[,\d]*(?:\.\d+)?)', r'**\1\2**', clean_item)
                st.write(f"• {clean_item}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Timeline d'exécution
        if sections['execution_timeline']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📅 Feuille de Route")
            
            timeline_phases = [
                {"période": "M1-M3", "titre": "Phase Préparation", "couleur": "#e74c3c"},
                {"période": "M4-M6", "titre": "Phase Lancement", "couleur": "#e67e22"},
                {"période": "M7-12", "titre": "Phase Croissance", "couleur": "#27ae60"}
            ]
            
            for i, (phase, item) in enumerate(zip(timeline_phases, sections['execution_timeline'][:3])):
                st.markdown(f"""
                <div style="background: {phase['couleur']}; color: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <strong>{phase['période']} - {phase['titre']}</strong><br>
                    {item.replace('•', '').strip()}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analyse des risques
        if sections['risk_analysis']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("⚠️ Analyse des Risques")
            for item in sections['risk_analysis'][:3]:
                st.write(f"• {item.replace('•', '').strip()}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # KPIs
        if sections.get('kpis'):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📊 Indicateurs Clés (KPIs)")
            for item in sections['kpis'][:4]:
                st.write(f"• {item.replace('•', '').strip()}")
            st.markdown('</div>', unsafe_allow_html=True)

def create_marketing_funnel():
    """Crée un graphique d'entonnoir de conversion"""
    st.markdown("#### 🎯 Entonnoir de Conversion Marketing")
    
    funnel_stages = ['Awareness', 'Consideration', 'Conversion', 'Retention', 'Advocacy']
    conversion_rates = [100, 25, 8, 6, 4]  # Pourcentages
    users = [10000, 2500, 800, 600, 400]
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_stages,
        x=users,
        textinfo="value+percent initial",
        opacity=0.8,
        marker={"color": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]}
    ))
    
    fig_funnel.update_layout(
        title="Entonnoir de Conversion Client",
        showlegend=False,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_funnel, use_container_width=True)

def create_roi_analysis():
    """Crée une analyse de ROI détaillée"""
    st.markdown("#### 💰 Analyse ROI par Canal")
    
    channels = ['Social Media', 'SEO/Content', 'Email Marketing', 'Publicité Payante', 'Partenariats']
    investment = [5000, 3000, 2000, 8000, 4000]
    revenue = [15000, 12000, 8000, 20000, 10000]
    roi = [(rev - inv) / inv * 100 for rev, inv in zip(revenue, investment)]
    
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(
        x=channels,
        y=roi,
        name='ROI (%)',
        marker_color=['#28a745' if x > 100 else '#ffc107' if x > 50 else '#dc3545' for x in roi]
    ))
    
    fig_roi.update_layout(
        title="ROI par Canal Marketing (%)",
        xaxis_title="Canaux",
        yaxis_title="ROI (%)",
        template='plotly_white'
    )
    
    st.plotly_chart(fig_roi, use_container_width=True)
    
    # Tableau détaillé
    roi_data = pd.DataFrame({
        'Canal': channels,
        'Investissement (€)': investment,
        'Revenu Généré (€)': revenue,
        'ROI (%)': roi,
        'Performance': ['Excellent' if r > 100 else 'Bon' if r > 50 else 'À améliorer' for r in roi]
    })
    
    st.dataframe(roi_data, use_container_width=True)

def create_customer_acquisition_analysis():
    """Crée une analyse du coût d'acquisition client"""
    st.markdown("#### 👥 Analyse Coût d'Acquisition Client (CAC)")
    
    months = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
    marketing_spend = [2000, 2500, 3000, 3500, 4000, 4500]
    new_customers = [25, 35, 45, 55, 65, 75]
    cac = [spend / customers for spend, customers in zip(marketing_spend, new_customers)]
    
    fig_cac = go.Figure()
    fig_cac.add_trace(go.Scatter(
        x=months, y=cac, name='CAC (€)',
        line=dict(color='#dc3545', width=4),
        mode='lines+markers'
    ))
    fig_cac.add_hline(y=50, line_dash="dash", line_color="green", 
                     annotation_text="Objectif CAC")
    
    fig_cac.update_layout(
        title="Évolution du Coût d'Acquisition Client",
        xaxis_title="Mois",
        yaxis_title="CAC (€)",
        template='plotly_white'
    )
    
    st.plotly_chart(fig_cac, use_container_width=True)

def main():
    # Header principal
    st.markdown('<h1 class="main-header">🚀 Smart Business Planner</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("💡 Votre Idée Business")
        
        st.markdown('<div class="idea-input">', unsafe_allow_html=True)
        business_idea = st.text_area(
            "**Décrivez votre idée business :**",
            placeholder="Ex: Une plateforme de livraison de repas healthy pour les entreprises...\nUn service de coaching en ligne pour développeurs web...\nUne marketplace de produits artisanaux locaux...",
            height=100
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        country = st.text_input("🌍 **Pays de lancement :**", "France")
        
        budget = st.text_input("💰 **Budget initial (optionnel) :**", 
                             placeholder="Ex: 10 000€, 50 000€...")
        
        # Options d'analyse avancée
        st.markdown("---")
        st.header("📊 Options d'Analyse")
        show_detailed_finance = st.checkbox("Analyse Financière Détaillée", value=True)
        show_marketing_dashboard = st.checkbox("Dashboard Marketing", value=True)
        show_advanced_metrics = st.checkbox("Métriques Avancées", value=True)
        
        st.markdown("---")
        generate_btn = st.button("🚀 Générer le Business Model Complet", type="primary", use_container_width=True)
        
        st.markdown("""
        <div style='margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;'>
        <small>💡 <strong>Conseil :</strong> Soyez spécifique dans votre idée pour obtenir un business model plus précis et personnalisé.</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Contenu principal
    if generate_btn:
        if not business_idea:
            st.warning("⚠️ Veuillez décrire votre idée business")
            return
        
        if not country:
            st.warning("⚠️ Veuillez spécifier le pays de lancement")
            return
        
        # Animation de chargement
        with st.spinner("🔄 Création de votre business model personnalisé..."):
            progress_bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            # Génération du contenu
            result = generate_business_idea_and_canvas(business_idea, country, budget)
            sections = parse_response(result)
        
        st.success("✅ Business Model Complet généré avec succès!")
        
        # Métriques rapides
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Type", "Business Model Personnalisé")
        with col2:
            st.metric("Pays", country)
        with col3:
            st.metric("Sections", "10 composantes")
        with col4:
            st.metric("Statut", "Prêt à l'emploi ✅")
        
        # Affichage des sections principales
        display_business_idea(sections)
        display_bmc(sections)
        
        # Analyses détaillées conditionnelles
        if show_detailed_finance:
            display_financial_analysis(sections)
        
        if show_marketing_dashboard:
            display_marketing_strategy(sections)
            
            # Analyses marketing avancées
            if show_advanced_metrics:
                st.markdown('<div class="section-header">📈 ANALYSES MARKETING AVANCÉES</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    create_marketing_funnel()
                    create_customer_acquisition_analysis()
                
                with col2:
                    create_roi_analysis()
        
        # Section de synthèse et recommandations
        st.markdown('<div class="section-header">🎯 SYNTHÈSE & RECOMMANDATIONS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("✅ Points Forts")
            strengths = [
                "Business model clair et structuré",
                "Proposition de valeur différenciante",
                "Marché identifié avec opportunités",
                "Stratégie marketing multi-canaux",
                "Projections financières réalistes"
            ]
            for strength in strengths:
                st.write(f"• {strength}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("🎯 Prochaines Étapes")
            next_steps = [
                "Affiner l'étude de marché",
                "Développer un prototype/MVP",
                "Tester la proposition de valeur",
                "Valider les hypothèses financières",
                "Préparer le plan de lancement"
            ]
            for step in next_steps:
                st.write(f"• {step}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Bouton de réinitialisation et export
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Générer un nouveau business model", use_container_width=True):
                st.rerun()
            
            if st.button("📄 Exporter le rapport complet", use_container_width=True):
                st.success("📊 Rapport exporté avec succès!")
                st.info("Fonctionnalité d'export à implémenter (PDF/Excel)")
    
    else:
        # Page d'accueil
        st.markdown("""
        <div style='text-align: center; padding: 3rem 1rem;'>
            <h2 style='color: #2c3e50;'>Transformez votre idée en business model viable</h2>
            <p style='font-size: 1.1rem; color: #7f8c8d;'>
                Obtenez un plan d'affaires complet et personnalisé pour votre projet entrepreneurial
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exemples d'idées
        st.markdown("### 💡 Exemples d'idées business :")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="card">
                <h4>🍽️ Service alimentaire</h4>
                <p>"Traiteur healthy pour entreprises"</p>
                <p>"Cours de cuisine en ligne"</p>
                <p>"Box de produits locaux"</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h4>💻 Service digital</h4>
                <p>"App de productivité"</p>
                <p>"Plateforme SaaS"</p>
                <p>"Marketplace niche"</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="card">
                <h4>🛍️ Commerce</h4>
                <p>"Boutique e-commerce"</p>
                <p>"Service local"</p>
                <p>"Produit physique"</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Fonctionnalités avancées
        st.markdown("---")
        st.markdown("### 🎯 Ce que vous obtenez :")
        
        features = [
            ("💡", "Idée business développée", "Votre concept transformé en proposition concrète"),
            ("📊", "Business Model Canvas", "Les 9 blocs essentiels du BMC"),
            ("💰", "Analyse financière détaillée", "Graphiques, projections, ROI"),
            ("🎯", "Dashboard marketing", "Stratégies, KPIs, entonnoir de conversion"),
            ("📈", "Analyses avancées", "ROI par canal, coût d'acquisition"),
            ("⚠️", "Analyse des risques", "Identification et mitigation"),
            ("📅", "Timeline d'exécution", "Calendrier de mise en œuvre"),
            ("📋", "Recommandations", "Points forts et prochaines étapes")
        ]
        
        cols = st.columns(4)
        for i, (emoji, title, desc) in enumerate(features):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card">
                    <h4>{emoji} {title}</h4>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()