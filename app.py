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
TOKEN_AUTH = "eyJhbGciOiJSUzI1NiIsImtpZCI6Im9OUVhqWXhvQ3ZscFVnVDdCQkdYTHhwUGxxT0k1c0lqWVdyQXhhWFpTczAiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiIzZTdkN2M2NDAxOWUwNDhiNjFlNTdmNjczZjAxYmU3MCIsImp0aSI6IjBkMTRiYzlhNWNhZTMzOTQ0NjFmOGRlYjlmMTljOWQyIiwiaXNzIjoiaHR0cHM6Ly9sZWdoZS5mYW50YWNhbGNpby5pdCIsImlhdCI6MTc4ODc5MjQyMCwiZXhwIjoxODIwMzI4NDIwLCJsX2lkIjoiNDE4MTgwNSIsI3RfaWQiOiIxOTE2NjAzNCIsInVzZXJfaWQiOiIzMzkwOTE1Iiwic3RfbGVhZ3VlcyI6IjE3ODg3OTI0MjA4NjciLCJzdF_hdXRoIjoiMTcyNjE3Mjc5NDM3MSIsInJvbGUiOiJ1c2VyX2xlYWd1ZSIsInRva2VuX3VzZSI6ImlkIiwibmJmIjoxNzg4NzkyNDIwLCJhdWQiOiJmYW50YWNhbGNpbyJ9.JUutJNUEvV0M6knMIDAPAwrwBC7_SRwjQNfh9jcEhVzE0N0bK17MdCJjiVY4H-siblvJ4NF7Dabf8v2lMdgZXdYq-UOEbxq-BxVxB5N0Mk6PiceQQm25W2Fsg1tAXZ-NSXe5ARIVmgH_-mcnkU8sZVtfcmkHn3Pgf2zunLYJxrMvLR6wn1QJq_v4IG8J231hKf3EJV55JQ40G9a9I7BMzAVqEVcBq5pKFO3Vq5lkZUyav0HJAIBbUakVrDATMx6zXfZTvygFIRfE7QTpg0vH4nHCcTW8c_Jyh8dqqBPmuWR6m-mZuk3Ga-ZewaIvNpQgTaJd7SEABfJcv9SmnLNxsg"
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

SYSTEM_PROMPT = (
    "Sei il Direttore supremo della Fantagazzetta FiordiLuce: un editorialista sportivo caustico, brillante, cinico e spietato. "
    "Commenta la classifica della lega analizzando gli spostamenti, i punti e i risultati appena calcolati della giornata. "
    "Inizia sempre il commento menzionando chi è in testa con frasi del tipo 'Oh guarda quello è primo, se la sta cavando, la sua squadra vale...' ma poi demolisci o loda gli altri in base a come si sono mossi in classifica. "
    "Vietato usare asterischi '*' o cancelletti '#'."
)

st.set_page_config(page_title="FiordiLuce League", page_icon="⚽", layout="centered")

# Stile CSS personalizzato (tema scuro, bordi dorati, stile FantaGazzetta)
st.markdown("""
    <style>
    .stApp { background-color: #030712; color: #f9fafb; }
    .sidebar .stSidebar { background-color: #0b0f19; }
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
    return {"pagellone": "", "rose": "", "pronostici": "", "processo": "", "classifica_commento": "", "ultima_classifica_str": ""}

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
        return f"Errore generazione Claude ({res.status_code})"
    except Exception as e:
        return f"Errore di connessione: {e}"

db = carica_archivio()

# =====================================================================
# BARRA LATERALE (SIDEBAR)
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
# CONTENUTO DELLE SEZIONI
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
    
    # Sincronizzazione automatica commento IA sulla classifica
    nuova_str = json.dumps(dati_classifica, sort_keys=True)
    vecchia_str = db.get("ultima_classifica_str", "")
    
    if nuova_str != vecchia_str or not db.get("classifica_commento"):
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
            <p style="font-size: 14px; line-height: 1.5;">{db.get("classifica_commento", "")}</p>
        </div>
    """, unsafe_allow_html=True)

else:
    # Sezioni dinamiche (Pagellone, Rose, Pronostici, Processo)
    config_sezioni = {
        "Il Pagellone dell'Asta": ("📜 Il Pagellone dell'Asta", "pagellone", "Scrivi il pagellone spietato e ironico dell'asta per tutte le squadre della lega FiordiLuce."),
        "Rose e Calciatori": ("👥 Rose e Calciatori", "rose", "Analizza le rose e i colpi di mercato dei vari presidenti nella lega FiordiLuce."),
        "Pronostici Pre-Partita": ("🔮 Pronostici Pre-Partita", "pronostici", "Spara i pronostici sfacciati e le previsioni catastrofiche per la prossima giornata."),
        "Il Processo del Lunedì": ("⚖️ Il Processo del Lunedì", "processo", "Conduci il processo del lunedì commentando voti, scandali e risultati della giornata appena conclusa.")
    }
    
    titolo_sezione, chiave_db, prompt_base = config_sezioni[scelta_menu]
    
    st.markdown(f"""
        <div class="gold-box">
            <h3 style="color: #f59e0b; margin-top: 0;">{titolo_sezione}</h3>
            <p style="color: #9ca3af; font-size: 12px;">Interroga la redazione per generare o aggiornare i contenuti editoriali.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Genera con IA Redazione", type="primary"):
        with st.spinner("Il Direttore sta scrivendo l'articolo..."):
            testo = chiama_claude(prompt_base)
            db[chiave_db] = testo
            salva_archivio(db)
            st.rerun()
            
    testo_attuale = db.get(chiave_db, "Nessun contenuto generato. Clicca il pulsante sopra per interrogare la redazione.")
    st.markdown(f"""
        <div style="background-color: #0b0f19; border: 1px solid #1f2937; border-radius: 10px; padding: 16px;">
            <p style="font-size: 14px; line-height: 1.5; white-space: pre-wrap;">{testo_attuale}</p>
        </div>
    """, unsafe_allow_html=True)