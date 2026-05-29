import os
import requests
from myproject.ai_service.app.services.ai_service import AIService

class RAGService:
    # A simple in-memory vector store for demonstration
    # In production, use ChromaDB, FAISS, or Pinecone
    _vector_store = {} # {course_id: [{"text": "...", "embedding": [...]}, ...]}
    _storage_path = "vector_store.json"

    @classmethod
    def _load_storage(cls):
        import json
        if os.path.exists(cls._storage_path):
            try:
                with open(cls._storage_path, "r", encoding="utf-8") as f:
                    cls._vector_store = json.load(f)
            except Exception:
                cls._vector_store = {}

    @classmethod
    def _save_storage(cls):
        import json
        with open(cls._storage_path, "w", encoding="utf-8") as f:
            json.dump(cls._vector_store, f)


    @staticmethod
    def get_embeddings(text):
        """Call Gemini Embedding API"""
        api_key = os.getenv("AI_API_KEY")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
        
        payload = {
            "model": "models/gemini-embedding-001",
            "content": {"parts": [{"text": text}]}
        }
        
        try:
            response = requests.post(f"{url}?key={api_key}", json=payload)
            result = response.json()
            return result['embedding']['values']
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0] * 768 # Fallback

    @classmethod
    def index_document(cls, course_id, text, metadata=None):
        """Chunk text and store embeddings with metadata"""
        cls._load_storage()
        chunks = [text[i:i+1000] for i in range(0, len(text), 800)] # Simple sliding window chunking
        
        if course_id not in cls._vector_store:
            cls._vector_store[course_id] = []
            
        for chunk in chunks:
            embedding = cls.get_embeddings(chunk)
            cls._vector_store[course_id].append({
                "text": chunk,
                "embedding": embedding,
                "metadata": metadata or {}
            })
        cls._save_storage()
        print(f"Indexed {len(chunks)} chunks for Course {course_id}")

    @classmethod
    def retrieve_context(cls, course_id, query, top_k=3):
        """Find most relevant chunks using simple dot product similarity"""
        cls._load_storage()
        query_embedding = cls.get_embeddings(query)
        docs = cls._vector_store.get(course_id, [])
        
        if not docs:
            return []

        # Calculate similarity (Manual dot product for simplicity)
        def similarity(v1, v2):
            if not v1 or not v2: return 0
            return sum(a * b for a, b in zip(v1, v2))

        scored_docs = []
        for doc in docs:
            score = similarity(query_embedding, doc['embedding'])
            scored_docs.append((score, doc))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return scored_docs[:top_k]

    @classmethod
    def answer_with_rag(cls, course_id, question):
        """The full RAG pipeline with Course Database Context and Video Segments"""
        from myproject.courses_service.app.models.courses import Course
        
        # 1. Fetch Course Metadata for basic context
        course_info = ""
        try:
            course = Course.objects.get(id=course_id)
            course_info = f"Khóa học: {course.title}\nMô tả: {course.description}\nĐề cương: {course.syllabus or 'N/A'}"
        except Exception:
            course_info = "Không tìm thấy thông tin khóa học cụ thể."

        # 2. Retrieve vector context
        scored_docs = cls.retrieve_context(course_id, question)
        
        context_parts = []
        video_refs = []
        for score, doc in scored_docs:
            context_parts.append(doc['text'])
            meta = doc.get('metadata', {})
            if meta.get('material_id'):
                raw_seconds = int(meta.get('start_time', 0))
                minutes = raw_seconds // 60
                seconds = raw_seconds % 60
                time_label = f"{minutes:02d}:{seconds:02d}"
                video_refs.append(f"- [Xem video tại {time_label}](material_{meta['material_id']}_{raw_seconds})")

        context_text = "\n---\n".join(context_parts)
        references = "\n".join(set(video_refs))
        
        prompt = f"""Bạn là trợ lý học tập AI chuyên biệt của UniLearn. 
NHIỆM VỤ: Chỉ trả lời các câu hỏi liên quan đến nội dung khóa học dưới đây. 

THÔNG TIN KHÓA HỌC:
{course_info}

BỔ SUNG NỘI DUNG CHI TIẾT (RAG):
{context_text if context_text else "Không có nội dung chi tiết bổ sung."}

QUY TẮC:
1. Nếu câu hỏi KHÔNG liên quan đến nội dung khóa học này, hãy trả lời: "Xin lỗi, tôi chỉ hỗ trợ giải đáp thắc mắc trong phạm vi khóa học này. Bạn có câu hỏi nào về {course.title if 'course' in locals() else 'khóa học'} không?"
2. Luôn trả lời bằng tiếng Việt, thân thiện và chuyên nghiệp.
3. Sử dụng Markdown để định dạng câu trả lời (in đậm, danh sách, khối mã nếu cần).
4. Nếu có thông tin video liên quan, hãy gợi ý người dùng xem đoạn video đó.

CÂU HỎI CỦA HỌC VIÊN:
{question}
"""
        answer = AIService.call_llm(prompt)
        
        if references:
            answer += f"\n\n**Tài liệu tham khảo:**\n{references}"
            
        return answer
