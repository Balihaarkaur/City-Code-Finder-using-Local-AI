import streamlit as st
import pandas as pd
import ollama
import difflib

# City code reference DB
CITY_CODE_DB = {
    'agra': 'AU-AGR',
    'delhi': 'AU-NTL',
    'bareilly': 'AU-BLY',
    'prayagraj': 'AU-ALD',
    'karnal': 'AU-KNL',
    'kanpur': 'AU-KNP',
    'lucknow': 'AU-LKO',
    'mumbai': 'AU-MUM',
    'bangalore': 'AU-BLR',
    'hyderabad': 'AU-HYD',
    'kolkata': 'AU-CCU',
    'meerut': 'AU-MRT',  # Fixed case
    'chennai': 'AU-MAA',
    'pune': 'AU-PNE',
    'jaipur': 'AU-JPR',
    'chandigarh': 'AU-CHD',
    'noida': 'AU-NOD',
    'gurgaon': 'AU-GGN',
    'surat': 'AU-SUR',
    'vadodara': 'AU-VAD',
    'coimbatore': 'AU-CBE',
    'indore': 'AU-IDR',
    'bhopal': 'AU-BPL',
    'nagpur': 'AU-NGP',
    'rajkot': 'AU-RJT',
    'vijayawada': 'AU-VJA',
    'cochin': 'AU-COK',
    'thiruvananthapuram': 'AU-TRV',
    'mangalore': 'AU-MNG',
    'amritsar': 'AU-AMR',
    'ludhiana': 'AU-LDH',
    'jalandhar': 'AU-JAL',
    'patna': 'AU-PAT',
    'ranchi': 'AU-RAN',
    'bhubaneswar': 'AU-BBS'   
}

def load_ollama_model():
    try:
        client = ollama.Client()
        # Quick test to see if Ollama is running
        client.list()
        return client
    except Exception:
        return None

def query_local_llm(city_input: str, client: ollama.Client) -> str:
    try:
        # First check if it's a direct abbreviation mapping
        abbrev_map = {
            'agr': 'agra',
            'dilli': 'delhi',
            'del': 'delhi',
            'mum': 'mumbai',
            'blr': 'bangalore',
            'bang': 'bangalore',
            'hyd': 'hyderabad',
            'lko': 'lucknow',
            'knp': 'kanpur',
            'chn': 'chennai',
            'kol': 'kolkata',
            'pun': 'pune',
            'jpr': 'jaipur',
            'ind': 'indore',
            'bpl': 'bhopal',
            'ngp': 'nagpur',
            'cok': 'cochin',
            'trv': 'thiruvananthapuram',
            'mrt': 'meerut',
            'mtt': 'meerut',  # Adding for your query
            'mer': 'meerut',
            'nod': 'noida',
            'ggn': 'gurgaon',
            'gur': 'gurgaon',
            'srt': 'surat',
            'vad': 'vadodara',
            'cbe': 'coimbatore',
            'idr': 'indore',
            'rjt': 'rajkot',
            'vja': 'vijayawada',
            'mng': 'mangalore',
            'amr': 'amritsar',
            'ldh': 'ludhiana',
            'jal': 'jalandhar',
            'pat': 'patna',
            'ran': 'ranchi',
            'bbs': 'bhubaneswar'
        }
        
        # Check direct abbreviation first
        if city_input.lower() in abbrev_map:
            return abbrev_map[city_input.lower()]
        
        # If Ollama is available, try AI
        if client:
            prompt = f"""You are an expert on Indian cities. Given the input '{city_input}', return ONLY the most likely Indian city name that matches.

Examples:
- agr -> agra
- dilli -> delhi
- mum -> mumbai
- blr -> bangalore
- bang -> bangalore
- hyd -> hyderabad
- mtt -> meerut
- mer -> meerut

Input: {city_input}
Answer with only the city name in lowercase:"""
            
            response = client.generate(
                model='llama3', 
                prompt=prompt,
                options={
                    'temperature': 0.0,  # Zero temperature for consistent results
                    'num_predict': 15,   # Allow slightly more tokens
                    'top_p': 0.1        # Very focused responses
                }
            )
            result = response['response'].strip().lower()
            
            # Clean up the response - extract only the city name
            result = result.split('\n')[0].split('.')[0].split(',')[0].split(' ')[0]
            result = ''.join(char for char in result if char.isalpha())  # Remove non-alphabetic chars
            
            return result if result else ""
        
        return ""
        
    except Exception as e:
        st.error(f"⚠️ LLM Error: {e}")
        return ""

def get_suggestions(city_input, db_keys):
    return difflib.get_close_matches(city_input, db_keys, n=3, cutoff=0.6)

def main():
    st.set_page_config(
        page_title="🏙️ AI City Code Finder",
        page_icon="🏙️",
        layout="wide"
    )

    st.title("🏙️ City Code Finder using Local AI")
    st.markdown("Enter a city name, abbreviation, or short code to find its standard city code. Uses offline Ollama AI to help if you're unsure.")

    # Check Ollama status
    client = load_ollama_model()
    if client:
        st.success("🤖 AI Assistant Ready (Ollama + Llama3)")
    else:
        st.error("🔌 AI Assistant Offline - Setup required:")
        st.markdown("""
        **To enable AI assistance:**
        1. Install Ollama: https://ollama.ai/
        2. Run: `ollama pull llama3`
        3. Restart this app
        """)

    city_input = st.text_input("🔍 Enter city name or abbreviation:", placeholder="e.g., agr, dilli, mum, lko...")

    if city_input:
        city_input_lower = city_input.strip().lower()

        # 1. Direct match in database
        if city_input_lower in CITY_CODE_DB:
            st.success(f"✅ Code for '{city_input}': **{CITY_CODE_DB[city_input_lower]}**")
            st.caption("🎯 Exact match from local database")

        else:
            # 2. Try built-in abbreviation mapping first
            ai_guess = query_local_llm(city_input_lower, client)
            
            if ai_guess and ai_guess in CITY_CODE_DB:
                st.success(f"✅ Code for '{ai_guess.title()}': **{CITY_CODE_DB[ai_guess]}**")
                if client:
                    st.caption("🧠 Found using AI interpretation")
                else:
                    st.caption("🔍 Found using built-in abbreviation mapping")

            # 3. Fuzzy logic fallback
            else:
                fuzzy_matches = get_suggestions(city_input_lower, list(CITY_CODE_DB.keys()))
                if fuzzy_matches:
                    st.info("🤔 No exact match found. Possible matches:")
                    for match in fuzzy_matches:
                        st.write(f"🔹 **{match.title()}** — {CITY_CODE_DB[match]}")
                else:
                    st.error("❌ No match found. Please check the reference table below or try a different spelling.")

    st.markdown("---")
    st.subheader("📋 City Code Reference Table")
    
    # Create a properly formatted dataframe for older Streamlit
    df = pd.DataFrame(list(CITY_CODE_DB.items()), columns=["City Name", "City Code"])
    df["City Name"] = df["City Name"].str.title()  # Capitalize city names
    df = df.sort_values("City Name").reset_index(drop=True)  # Sort alphabetically and reset index
    
    # Add row numbers starting from 1
    df.index = df.index + 1
    
    # Display the table
    st.table(df)

if __name__ == "__main__":
    main()
