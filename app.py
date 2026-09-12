import json
import os
import requests
import streamlit as st

# =====================================================================
# CONFIGURAZIONE & CREDENZIALI
# =====================================================================
DB_FILE = "bacheca_dati.json"
ID_LEGA = "4181805"
APP_KEY_FC = "ICiELOObd5DF5uJEATi77CRvHiiRuMU0"
TOKEN_AUTH = "eyJhbGciOiJSUzI1NiIsImtpZCI6Im9OUVhqWXhvQ3ZscFVnVDdCQkdYTHhwUGxxT0k1c0lqWVdyQXhhWFpTczAiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiIzZTdkN2M2NDAxOWUwNDhiNjFlNTdmNjczZjAxYmU3MCIsImp0aSI6IjBkMTRiYzlhNWNhZTMzOTQ0NjFmOGRlYjlmMTljOWQyIiwiaXNzIjoiaHR0cHM6Ly9sZWdoZS5mYW50YWNhbGNpby5pdCIsImlhdCI6MTc4ODc5MjQyMCwiZXhwIjoxODIwMzI4NDIwLCJsX2lkIjoiNDE4MTgwNSIsI3RfaWQiOiIxOTE2NjAzNCIsInVzZXJfaWQiOiIzMzkwOTE1Iiwic3RfbGVhZ3VlcyI6IjE3ODg3OTI0MjA4NjciLCJzdF9hdXRoIjoiMTcyNjE3Mjc5NDM3MSIsInJvbGUiOiJ1c2VyX2xlYWd1ZSIsInRva2VuX3VzZSI6ImlkIiwibmJmIjoxNzg4NzkyNDIwLCJhdWQiOiJmYW50YWNhbGNpbyJ9.JUutJNUEvV0M6knMIDAPAwrwBC7_SRwjQNfh9jcEhVzE0N0bK17MdCJjiVY4H-siblvJ4NF7Dabf8v2lMdgZXdYq-UOEbxq-BxVxB5N0Mk6PiceQQm25W2Fsg1tAXZ-NSXe5ARIVmgH_-mcnkU8sZVtfcmkHn3Pgf2zunLYJxrMvLR6wn1QJq_v4IG8J231hKf3EJV55JQ40G9a9I7BMzAVqEVcBq5pKFO3Vq5lkZUyav0HJAIBbUakVrDATMx6zXfZTvygFIRfE7QTpg0vH4nHCcTW8c_Jyh8dqqBPmuWR6m-mZuk3Ga-ZewaIvNpQgTaJd7SEABfJcv9SmnLNxsg"
CLAUDE_API_KEY = "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"

squadre_dati_base = {
    "19162484": {"nome": "Atletico Poco", "pres": "Mr Lasagna"},
    "19163180": {"nome": "Real Inps Team", "pres": "cristy1965"},
    "19164907": {"nome": "AC ciughina", "pres": "Giovanni"},
    "19166034": {"nome": "SAPPINIGHI", "pres": "Franco"},
    "19210141": {"nome": "sviolinata", "pres": "fabietto"},
    "19504860": {"nome": "OComeLeAndahaa FC", "pres": "HAIGIAVINTOTU"},
    "19555509": {"nome": "Real sculata", "pres": "Pando"},
    "19587401": {"nome": "real marotta", "pres": "Alessio"},
    "19588409": {"nome": "Herta vernello", "pres": "Fefino / Sandrino"},
    "19667036": {"nome": "giuardiaeladri", "pres": "Alessandro Magli"}
}

# Dati di esempio dettagliati per le rose (strutturati puliti)
rose_dettaglio = {
    "Atletico Poco": {
        "bilancio": "466 crediti", "record": "70 crediti",
        "portieri": ["Perri (1cr)", "Stankovic F. (9cr)", "Skorupski (6cr)"],
        "difensori": ["Valeri (1cr)", "Dimarco (70cr)", "Bellanova (1cr)", "Valdepenas (5cr)", "Belghali (1cr)", "Marcandalli (6cr)", "Valle (10cr)", "Kaiki (1cr)"],
        "centrocampisti": ["Taylor K. (10cr)", "Bernardeschii (2cr)", "McTominay (26cr)", "Ederson D.S. (22cr)", "Orsolini (46cr)", "Zalewski (1cr)", "Calhanoglu (40cr)", "Perrone (4cr)"],
        "attaccanti": ["Dybala (41cr)", "Laurientè (21cr)", "Simeone (56cr)", "Bowie (4cr)", "Pinamonti (66cr)", "Piccoli (16cr)"]
    }
}

SYSTEM_PROMPT = (
    "Sei il Direttore supremo della Fantagazzetta FiordiLuce: un editorialista sportivo caustico, brillante, cinico e spietato. "
    "Commenta la classifica della lega analizzando gli spostamenti, i punti e i risultati appena calcolati della giornata. "
    "Inizia sempre il commento menzionando chi è in testa con frasi del tipo 'Oh guarda quello è primo, se la sta cavando, la sua squadra vale...' ma poi demolisci o loda gli altri in base a come si sono mossi in classifica. "
    "Vietato usare asterischi '*' o cancelletti '#'."
)

st.set_page_config(page_title="FiordiLuce League", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #030712; color: #f9fafb; }
    .gold-box {
        background-color: #0b0f19;
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .team-card {
        background-color: #0b0f19;
        border: 1.5px solid #f59e0b;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .ai-badge {
        background-color: #064e3b;
        color: #22c55e;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def carica_archivio():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "pagellone": "Genera il pagellone tramite la redazione.",
        "rose": "Seleziona una squadra per visualizzare l'analisi dettagliata.",
        "pronostici": "Nessun pronostico disponibile.",
        "processo": "Il tribunale del lunedì non è ancora convocato.",
        "classifica_commento": "In attesa di dati ufficiali dalla Lega.",
        "ultima_classifica_str": ""
    }

def salva_archivio(dati):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def chiama_api_fantalega(endpoint_path):
    url = f"https://leghi.fantacalcio.it/api/{endpoint_path}"
    headers = {"app-key": APP_KEY_FC, "Authorization": f"Bearer {TOKEN_AUTH}", "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def ottieni_classifica_live():
    dati_api = chiama_api_fantalega(f"leagues/{ID_LEGA}/ranking")
    classifica_pulita = []
    if dati_api and isinstance(dati_api, list):
        for item in dati_api:
            team_id = str(item.get("team_id") or item.get("id", ""))
            base = squadre_dati_base.get(team_id, {})
            classifica_pulita.append({
                "pos": item.get("position") or item.get("pos", len(classifica_pulita) + 1),
                "nome": item.get("name") or item.get("team_name") or base.get("nome", "Squadra"),
                "pres": item.get("president") or item.get("pres") or base.get("pres", "N/D"),
                "punti": item.get("points") or item.get("pt", 0),
                "totale_fanta": item.get("total_score") or item.get("fanta_totale", 0.0)
            })
    if not classifica_pulita:
        for idx, (k, v) in enumerate(squadre_dati_base.items(), 1):
            classifica_pulita.append({"pos": idx, "nome": v["nome"], "pres": v["pres"], "punti": 0, "totale_fanta": 0.0})
    classifica_pulita.sort(key=lambda x: (x["punti"], x["totale_fanta"]), reverse=True)
    for idx, item in enumerate(classifica_pulita, 1):
        item["pos"] = idx
    return classifica_pulita

def chiama_claude(prompt_testo):
    headers = {"x-api-key": CLAUDE_API_KEY.strip(), "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt_testo}]
    }
    try:
        res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=25)
        if res.status_code == 200:
            dati = res.json()
            testo = "".join([b["text"] for b in dati.get("content", []) if b.get("type") == "text"])
            return testo.replace("*", "").replace("#", "")
        elif res.status_code == 401:
            return "Errore 401: Chiave API di Claude non valida o scaduta. Controlla la tua chiave nelle impostazioni."
        return f"Errore generazione Claude ({res.status_code})"
    except Exception as e:
        return f"Errore di connessione: {e}"

db = carica_archivio()

# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("### ⚽ FANTA GAZZETTA")
    st.markdown('<div class="ai-badge">✓ IA Claude Connessa</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    scelta_menu = st.radio(
        "Navigazione",
        ["Home Dashboard", "Classifica Ufficiale", "Il Pagellone dell'Asta", "Rose e Calciatori", "Pronostici Pre-Partita", "Il Processo del Lunedì"]
    )
    
    st.markdown("---")
    st.markdown("<p style='color: #9ca3af; font-size: 11px;'>Lega a 10 Squadre • ID 4181805<br>Stagione 2026/2027</p>", unsafe_allow_html=True)

# =====================================================================
# SEZIONI APP
# =====================================================================
if scelta_menu == "Home Dashboard":
    st.markdown("""
        <div class="gold-box" style="text-align: center;">
            <h3 style="color: #f59e0b; margin: 0;">★ ★ ★ ★ ★</h3>
            <h2 style="color: #f9fafb; margin: 5px 0;">FANTAGAZZETTA FIORDILUCE LEAGUE</h2>
        </div>
    """, unsafe_allow_html=True)
    
    for k, v in squadre_dati_base.items():
        st.markdown(f"""
            <div class="team-card">
                <b>🏷️ {v['nome']} — Pres. {v['pres']}</b>
                <hr style="border-color: #f59e0b; margin: 8px 0;">
                <p style="margin: 4px 0; font-size: 14px;">• VOTO ALLA ROSA: 6/10</p>
                <p style="margin: 4px 0; font-size: 14px;">• ANALISI DEL DIRETTORE: Mercato condotto nel caos totale.</p>
                <p style="margin: 4px 0; font-size: 14px;">• TOP E BIDONE: N/D</p>
                <p style="margin: 4px 0; font-size: 13px; font-style: italic; color: #d1d5db;">• SENTENZA STAGIONALE: In lotta per non retrocedere.</p>
            </div>
        """, unsafe_allow_html=True)

elif scelta_menu == "Classifica Ufficiale":
    st.markdown("""
        <div class="gold-box" style="text-align: center;">
            <h2 style="color: #f59e0b; margin: 0;">🏆 CLASSIFICA UFFICIALE LIVE</h2>
            <p style="color: #9ca3af; font-size: 12px; font-style: italic; margin-top: 5px;">Sincronizzata in tempo reale con la Lega Fantacalcio</p>
        </div>
    """, unsafe_allow_html=True)
    
    dati_classifica = ottieni_classifica_live()
    
    for item in dati_classifica:
        border_color = "#f59e0b" if item['pos'] == 1 else "#1f2937"
        st.markdown(f"""
            <div style="background-color: #0b0f19; border: 1px solid {border_color}; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #f59e0b; font-weight: bold; font-size: 16px; margin-right: 12px;">#{item['pos']}</span>
                    <b>{item['nome']}</b><br>
                    <span style="color: #9ca3af; font-size: 11px; font-style: italic;">Pres. {item['pres']}</span>
                </div>
                <div style="text-align: right;">
                    <span style="color: #22c55e; font-weight: bold; font-size: 15px;">{item['punti']} pt</span><br>
                    <span style="color: #9ca3af; font-size: 11px;">Tot: {item['totale_fanta']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Sincronizzazione automatica e persistente del commento IA sulla classifica
    nuova_str = json.dumps(dati_classifica, sort_keys=True)
    vecchia_str = db.get("ultima_classifica_str", "")
    
    if nuova_str != vecchia_str or not db.get("classifica_commento") or "Errore" in db.get("classifica_commento", ""):
        with st.spinner("La redazione sta analizzando i nuovi spostamenti in classifica..."):
            nomi_str = ", ".join([f"#{i['pos']} {i['nome']} ({i['punti']} pt)" for i in dati_classifica])
            prompt = (
                f"Ecco la classifica aggiornata in tempo reale della lega FiordiLuce: {nomi_str}. "
                "Analizza i nuovi spostamenti e i punteggi con il tuo stile caustico. "
                "Inizia tassativamente dicendo 'Oh guarda quello è primo, se la sta cavando, la sua squadra vale...' riferendoti alla prima in classifica, "
                "e poi commenta i movimenti e gli scivoloni degli altri presidenti."
            )
            testo_ia = chiama_claude(prompt)
            db["classifica_commento"] = testo_ia
            db["ultima_classifica_str"] = nuova_str
            salva_archivio(db)
            
    st.markdown(f"""
        <div class="gold-box" style="margin-top: 20px;">
            <h4 style="color: #f59e0b; margin-top: 0;">✍️ Commento del Direttore sui Verdetti</h4>
            <hr style="border-color: #f59e0b; margin: 8px 0;">
            <p style="font-size: 14px; line-height: 1.5; white-space: pre-wrap;">{db.get("classifica_commento", "")}</p>
        </div>
    """, unsafe_allow_html=True)

elif scelta_menu == "Rose e Calciatori":
    st.markdown("""
        <div class="gold-box">
            <h3 style="color: #f59e0b; margin: 0;">👥 Rose e Calciatori</h3>
            <p style="color: #9ca3af; font-size: 12px; margin-top: 4px;">Seleziona la squadra da esaminare:</p>
        </div>
    """, unsafe_allow_html=True)
    
    squadra_selezionata = st.selectbox("Seleziona squadra", list(squadre_dati_base.values()), format_func=lambda x: f"{x['nome']} (Pres. {x['pres']})")
    
    st.markdown(f"""
        <div class="team-card">
            <h3 style="color: #f59e0b; margin-top: 0;">{squadra_selezionata['nome']} — Pres. {squadra_selezionata['pres']}</h3>
            <p style="color: #9ca3af; font-size: 12px; margin-bottom: 4px;">• BILANCIO ASTA: 466 crediti | • ACQUISTO RECORD: 70 crediti</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("### 🟡 PORTIERI")
        st.markdown("- Perri (1cr)\n- Stankovic F. (9cr)\n- Skorupski (6cr)")
    with col2:
        st.markdown("### 🟢 DIFENSORI")
        st.markdown("- Valeri (1cr)\n- Dimarco (70cr)\n- Bellanova (1cr)\n- Valdepenas (5cr)\n- Belghali (1cr)\n- Marcandalli (6cr)")
    with col3:
        st.markdown("### 🔵 CENTROCAMPISTI")
        st.markdown("- Taylor K. (10cr)\n- Bernardeschi (2cr)\n- McTominay (26cr)\n- Ederson D.S. (22cr)\n- Orsolini (46cr)\n- Calhanoglu (40cr)")
    with col4:
        st.markdown("### 🔴 ATTACCANTI")
        st.markdown("- Dybala (41cr)\n- Laurientè (21cr)\n- Simeone (56cr)\n- Pinamonti (66cr)\n- Piccoli (16cr)")

else:
    config_sezioni = {
        "Il Pagellone dell'Asta": ("📜 Il Pagellone dell'Asta", "pagellone", "Scrivi il pagellone spietato e ironico dell'asta per tutte le squadre della lega FiordiLuce."),
        "Pronostici Pre-Partita": ("🔮 Pronostici Pre-Partita", "pronostici", "Spara i pronostici sfacciati e le previsioni catastrofiche per la prossima giornata."),
        "Il Processo del Lunedì": ("⚖️ Il Processo del Lunedì", "processo", "Conduci il processo del lunedì commentando voti, scandali e risultati della giornata appena conclusa.")
    }
    
    titolo_sezione, chiave_db, prompt_base = config_sezioni[scelta_menu]
    
    st.markdown(f"""
        <div class="gold-box">
            <h3 style="color: #f59e0b; margin-top: 0;">{titolo_sezione}</h3>
            <p style="color: #9ca3af; font-size: 12px;">Contenuti editoriali della redazione:</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Se il testo è vuoto o di default, lo genera in automatico la prima volta
    if not db.get(chiave_db) or "Genera" in db.get(chiave_db, "") or "attendere" in db.get(chiave_db, ""):
        with st.spinner("Il Direttore sta scrivendo l'articolo in automatico..."):
            testo = chiama_claude(prompt_base)
            db[chiave_db] = testo
            salva_archivio(db)
            
    if st.button("Rigenera con IA Redazione", type="primary"):
        with st.spinner("Aggiornamento in corso..."):
            testo = chiama_claude(prompt_base)
            db[chiave_db] = testo
            salva_archivio(db)
            st.rerun()
            
    st.markdown(f"""
        <div style="background-color: #0b0f19; border: 1px solid #1f2937; border-radius: 10px; padding: 16px;">
            <p style="font-size: 14px; line-height: 1.5; white-space: pre-wrap;">{db.get(chiave_db, "")}</p>
        </div>
    """, unsafe_allow_html=True)
