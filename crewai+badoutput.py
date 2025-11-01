import openai
import os
from colorama import Fore, Style, Back, init
import textwrap
import time
import re
import streamlit as st
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

# Initialisation de colorama pour la coloration Windows
init(autoreset=True)

# Configuration OpenRouter
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]

# Configuration LLM pour CrewAI
# Alternative si la première méthode ne fonctionne pas
llm_config = {
    "model": "openai/gpt-3.5-turbo",  # Modèle gratuit disponible sur OpenRouter
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.environ["OPENROUTER_API_KEY"],
    "headers": {
        "HTTP-Referer": "https://your-site.com",  # Optionnel mais recommandé
        "X-Title": "Business Plan Generator"      # Optionnel mais recommandé
    }
}

class BusinessCrew:
    """CrewAI pour générer un plan d'affaires complet"""
    
    def __init__(self, budget, business_idea, country, sector):
        self.budget = budget
        self.business_idea = business_idea
        self.country = country
        self.sector = sector
        
    def create_agents(self):
        """Crée les agents spécialisés avec configuration LLM"""
        
        # Configuration LLM commune pour tous les agents
        llm = LLM(**llm_config)
        
        # Agent 1: Expert Business Model Canvas
        self.bmc_agent = Agent(
            role="Expert en Business Model Canvas",
            goal="Créer un Business Model Canvas détaillé et innovant",
            backstory="""Tu es un consultant stratégique expert en modèles d'affaires innovants. 
            Tu as aidé plus de 100 startups à structurer leur business model avec une approche 
            pratique et orientée résultats.""",
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
        
        # Agent 2: Analyste Financier
        self.financial_agent = Agent(
            role="Analyste Financier Senior",
            goal="Produire une analyse financière réaliste et des projections précises",
            backstory="""Tu es un analyste financier expérimenté avec 15 ans d'expérience dans 
            l'analyse de startups et PME. Tu es expert en modélisation financière et en étude 
            de marché pour différents secteurs.""",
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
        
        # Agent 3: Stratège Marketing
        self.marketing_agent = Agent(
            role="Stratège Marketing Digital",
            goal="Développer une stratégie marketing complète et actionnable",
            backstory="""Tu es un expert en marketing digital et stratégie de marque. Tu as 
            lancé avec succès plus de 50 produits et services sur différents marchés, avec 
            une approche data-driven et créative.""",
            allow_delegation=False,
            verbose=True,
            llm=llm
        )
        
        # Agent 4: Chef de projet (pour orchestrer)
        self.manager_agent = Agent(
            role="Chef de Projet Business",
            goal="Coordonner l'ensemble des experts pour produire un plan d'affaires cohérent",
            backstory="""Tu es un chef de projet expérimenté spécialisé dans le lancement 
            de nouvelles entreprises. Tu excelles dans la synthèse et la coordination 
            d'équipes multidisciplinaires.""",
            allow_delegation=True,
            verbose=True,
            llm=llm
        )
    
    def create_tasks(self):
        """Crée les tâches pour chaque agent"""
        
        # Tâche 1: Business Model Canvas
        self.bmc_task = Task(
            description=f"""
            Crée un Business Model Canvas COMPLET et DÉTAILLÉ pour:
            - Idée: {self.business_idea}
            - Secteur: {self.sector}
            - Pays: {self.country}
            - Budget: {self.budget}
            
            Produis un BMC structuré avec:
            1. Proposition de valeur unique
            2. Segments clients détaillés
            3. Canaux de distribution
            4. Relations clients
            5. Flux de revenus réalistes
            6. Structure de coûts
            7. Ressources clés
            8. Activités principales
            9. Partenariats stratégiques
            
            Sois concret avec des chiffres réalistes adaptés au budget {self.budget}.
            Formatte la réponse en markdown avec des sections claires.
            """,
            agent=self.bmc_agent,
            expected_output="Un Business Model Canvas complet avec 9 blocs détaillés en format markdown"
        )
        
        # Tâche 2: Analyse Financière
        self.financial_task = Task(
            description=f"""
            Réalise une analyse financière COMPLÈTE pour:
            - Idée: {self.business_idea}
            - Secteur: {self.sector}
            - Budget initial: {self.budget}
            - Marché: {self.country}
            
            Inclus:
            1. Projections financières sur 3 ans (tableaux)
            2. Analyse du marché et de la concurrence
            3. Stratégie de prix détaillée
            4. Plan de financement
            5. Point de rentabilité
            6. Analyse des risques
            7. Recommandations budgétaires
            
            Base tes chiffres sur le budget {self.budget} et sois réaliste.
            Utilise des tableaux markdown pour les données financières.
            """,
            agent=self.financial_agent,
            expected_output="Une analyse financière détaillée avec projections, tableaux et recommandations en markdown"
        )
        
        # Tâche 3: Stratégie Marketing
        self.marketing_task = Task(
            description=f"""
            Développe une stratégie marketing COMPLÈTE pour:
            - Produit: {self.business_idea}
            - Secteur: {self.sector}
            - Budget: {self.budget}
            - Cible: {self.country}
            
            Crée un plan couvrant:
            1. Stratégie de lancement par phases
            2. Mix marketing (4P)
            3. Plan digital et canaux
            4. Budget marketing détaillé
            5. Calendrier éditorial
            6. KPI de performance
            7. Stratégie de contenu
            8. Positionnement de marque
            
            Adapte la stratégie au budget {self.budget}.
            Structure la réponse en sections markdown claires.
            """,
            agent=self.marketing_agent,
            expected_output="Un plan marketing complet avec stratégie, budget et calendrier en format markdown"
        )
        
        # Tâche 4: Synthèse finale
        self.final_task = Task(
            description=f"""
            Synthétise les travaux des experts pour créer un plan d'affaires COHÉRENT et PROFESSIONNEL pour:
            - Idée: {self.business_idea}
            - Secteur: {self.sector} 
            - Pays: {self.country}
            - Budget: {self.budget}
            
            Intègre harmonieusement:
            - Le Business Model Canvas
            - L'analyse financière
            - La stratégie marketing
            
            Assure la cohérence entre toutes les parties et produis un document final structuré en markdown.
            Crée un document bien formaté avec une table des matières.
            """,
            agent=self.manager_agent,
            expected_output="Un plan d'affaires complet et intégré avec les 3 composantes principales en format markdown",
            output_file="plan_affaires_complet.md"
        )
    
    def run_crew(self):
        """Exécute la crew et retourne les résultats"""
        try:
            self.create_agents()
            self.create_tasks()
            
            crew = Crew(
                agents=[self.bmc_agent, self.financial_agent, self.marketing_agent, self.manager_agent],
                tasks=[self.bmc_task, self.financial_task, self.marketing_task, self.final_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            return result
            
        except Exception as e:
            return f"Erreur lors de l'exécution: {str(e)}"

def setup_streamlit_ui():
    """Configure l'interface Streamlit moderne"""
    st.set_page_config(
        page_title="Business Plan Generator - CrewAI",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personnalisé pour une interface moderne
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
    }
    .result-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .agent-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .budget-high {
        border-left: 5px solid #28a745;
    }
    .budget-medium {
        border-left: 5px solid #ffc107;
    }
    .budget-low {
        border-left: 5px solid #dc3545;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

def get_budget_class(budget_str):
    """Détermine la classe CSS en fonction du budget"""
    try:
        # Extraction du nombre du budget
        budget_num = int(''.join(filter(str.isdigit, budget_str.split()[0])))
        if budget_num >= 100000:
            return "budget-high"
        elif budget_num >= 50000:
            return "budget-medium"
        else:
            return "budget-low"
    except:
        return "budget-medium"

def main_streamlit():
    """Version principale avec interface Streamlit et CrewAI"""
    setup_streamlit_ui()
    
    # Header principal
    st.markdown('<h1 class="main-header">🚀 BUSINESS PLAN GENERATOR - CREWAI</h1>', unsafe_allow_html=True)
    st.markdown("### 4 Agents Experts Génèrent Votre Plan d'Affaires Complet")
    
    # Initialisation de la session state
    if 'generate' not in st.session_state:
        st.session_state.generate = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {}

    # Section de configuration
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("### 📋 Informations du Projet")
        
        col1, col2 = st.columns(2)
        
        with col1:
            budget = st.text_input(
                "💰 Budget de départ", 
                placeholder="Ex: 50 000 €, 100 000 $, 25k EUR",
                help="Indiquez votre budget initial pour le projet"
            )
            
            business_idea = st.text_area(
                "💡 Idée Business", 
                placeholder="Décrivez votre idée d'entreprise en quelques phrases...",
                height=100,
                help="Décrivez clairement votre concept d'entreprise"
            )
        
        with col2:
            country = st.text_input(
                "🌍 Pays cible", 
                placeholder="Ex: France, Canada, Maroc...",
                help="Pays où vous souhaitez lancer votre entreprise"
            )
            
            sector = st.text_input(
                "🏢 Secteur d'activité", 
                placeholder="Ex: Technologie, Restauration, E-commerce...",
                help="Secteur principal de votre entreprise"
            )
        
        # Bouton de lancement
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            generate_disabled = not all([budget, business_idea, country, sector])
            if st.button("🚀 Générer le Plan d'Affaires Complet", 
                        type="primary", 
                        use_container_width=True,
                        disabled=generate_disabled):
                
                if all([budget.strip(), business_idea.strip(), country.strip(), sector.strip()]):
                    st.session_state.user_inputs = {
                        'budget': budget,
                        'business_idea': business_idea,
                        'country': country,
                        'sector': sector
                    }
                    st.session_state.generate = True
                    st.session_state.results = None
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Affichage des résultats
    if st.session_state.generate:
        # Afficher les informations saisies
        st.markdown("### 📊 Récapitulatif de Votre Projet")
        
        budget_class = get_budget_class(st.session_state.user_inputs['budget'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="agent-card {budget_class}">
                <h4>💰 Budget</h4>
                <p><strong>{st.session_state.user_inputs['budget']}</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="agent-card">
                <h4>💡 Idée</h4>
                <p>{st.session_state.user_inputs['business_idea'][:50]}...</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="agent-card">
                <h4>🌍 Pays</h4>
                <p><strong>{st.session_state.user_inputs['country']}</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="agent-card">
                <h4>🏢 Secteur</h4>
                <p><strong>{st.session_state.user_inputs['sector']}</strong></p>
            </div>
            """, unsafe_allow_html=True)

        # Génération avec CrewAI
        if st.session_state.results is None:
            with st.spinner("🔄 Lancement des agents CrewAI..."):
                # Afficher le statut des agents
                st.markdown("### 🤖 Équipe d'Agents en Action")
                
                agents_col1, agents_col2, agents_col3, agents_col4 = st.columns(4)
                
                with agents_col1:
                    st.markdown("""
                    <div class="agent-card">
                        <h4>🎯 Expert BMC</h4>
                        <p>Création du business model...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with agents_col2:
                    st.markdown("""
                    <div class="agent-card">
                        <h4>📊 Analyste Financier</h4>
                        <p>Calcul des projections...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with agents_col3:
                    st.markdown("""
                    <div class="agent-card">
                        <h4>🚀 Stratège Marketing</h4>
                        <p>Élaboration de la stratégie...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with agents_col4:
                    st.markdown("""
                    <div class="agent-card">
                        <h4>👨‍💼 Chef de Projet</h4>
                        <p>Coordination et synthèse...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Barre de progression
                progress_bar = st.progress(0)
                
                # Lancement de la CrewAI
                try:
                    crew = BusinessCrew(
                        budget=st.session_state.user_inputs['budget'],
                        business_idea=st.session_state.user_inputs['business_idea'],
                        country=st.session_state.user_inputs['country'],
                        sector=st.session_state.user_inputs['sector']
                    )
                    
                    # Simulation de progression
                    for i in range(4):
                        progress_bar.progress((i + 1) * 25)
                        time.sleep(0.5)  # Réduction du temps d'attente
                    
                    # Exécution réelle
                    result = crew.run_crew()
                    
                    progress_bar.progress(100)
                    st.session_state.results = result
                    
                    st.success("✅ Génération terminée avec succès!")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")
                    st.session_state.results = f"Erreur: {str(e)}"

        # Affichage des résultats
        if st.session_state.results and "Erreur" not in str(st.session_state.results):
            st.markdown("### 📄 Plan d'Affaires Généré")
            
            # Sections du résultat
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            
            # Affichage brut du résultat
            st.markdown("#### 🎯 Résultat Complet")
            st.markdown(str(st.session_state.results))
            
            # Boutons de téléchargement
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            
            with col_dl1:
                st.download_button(
                    label="📥 Télécharger le Rapport",
                    data=str(st.session_state.results),
                    file_name=f"plan_affaires_{st.session_state.user_inputs['sector']}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            
            with col_dl2:
                if st.button("🔄 Régénérer", use_container_width=True):
                    st.session_state.results = None
                    st.rerun()
            
            with col_dl3:
                if st.button("🗑️ Nouveau Projet", use_container_width=True):
                    st.session_state.generate = False
                    st.session_state.results = None
                    st.session_state.user_inputs = {}
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Section d'information
    with st.sidebar:
        st.header("ℹ️ À Propos")
        st.markdown("""
        **Fonctionnalités:**
        - 🎯 Business Model Canvas
        - 📊 Analyse financière  
        - 🚀 Stratégie marketing
        - 👨‍💼 Synthèse professionnelle
        
        **Technologies:**
        - CrewAI pour l'orchestration
        - LLM avancé pour la génération
        - Interface Streamlit moderne
        """)
        
        st.header("⚙️ Configuration")
        st.info("Agents: 4 spécialisés")
        st.info(f"Modèle: {llm_config['model']}")
        st.info("API: OpenRouter")

if __name__ == "__main__":
    main_streamlit()