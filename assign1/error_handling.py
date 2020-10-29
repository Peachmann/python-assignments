import string as st

def verify_input(text):
    uppercase = st.ascii_uppercase
    
    for c in text:
        if c not in uppercase:
            return False
    
    return True