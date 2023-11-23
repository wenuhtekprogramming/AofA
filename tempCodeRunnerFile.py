def cosine_similarity_score(user_answer, correct_answer):
    vectorizer = TfidfVectorizer() # Initializing TF-IDF Vectorizer
    tfidf_matrix = vectorizer.fit_transform([user_answer, correct_answer]) # Transforming text to TF-IDF matrix
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2]) # Calculating cosine similarity
    return cosine_sim[0][0] # Ret