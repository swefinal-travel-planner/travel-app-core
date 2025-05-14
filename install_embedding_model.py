from sentence_transformers import SentenceTransformer

model_name = "AITeamVN/Vietnamese_Embedding"
model_path = "./model_ai/vietnamese_embedding"

model = SentenceTransformer(model_name)
model.save(model_path)