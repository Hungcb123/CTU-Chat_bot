import asyncio
import logging
import httpx
from pathlib import Path
from typing import Optional

# Cấu hình Logging chuẩn Production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("LlamaParseClient")

class LlamaParseAsyncClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key không được để trống.")
            
        self.api_key = api_key
        self.base_url = "https://api.cloud.llamaindex.ai/api/parsing"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    async def parse_pdf_to_markdown(self, file_path: str | Path) -> str:
        """
        Entry point: Điều phối luồng Upload -> Poll Status -> Fetch Result.
        Sử dụng Async Context Manager để đảm bảo tự động dọn dẹp kết nối mạng.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")

        logger.info(f"Bắt đầu xử lý file [{path.name}] lên LlamaParse...")
        
        # Timeout 60s cho các tác vụ upload/download nặng
        async with httpx.AsyncClient(timeout=60.0, headers=self.headers) as client:
            try:
                # Bước 1: Upload file (Trigger Asynchronous Job)
                job_id = await self._upload_document(client, path)
                
                # Bước 2: Chờ đợi hệ thống xử lý (Exponential Backoff)
                await self._wait_for_job_completion(client, job_id)
                
                # Bước 3: Kéo dữ liệu Markdown về
                return await self._fetch_markdown_result(client, job_id)
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"Lỗi giao tiếp với LlamaParse: {e}")
            except Exception as e:
                logger.error(f"Lỗi hệ thống bất ngờ: {e}")
                raise

    async def _upload_document(self, client: httpx.AsyncClient, file_path: Path) -> str:
        url = f"{self.base_url}/upload"
        
        # Cấu hình OCR Tiếng Việt và bật Premium Mode (dành cho file Scan ảnh)
        data = {
            "language": "vi",
            "premium_mode": "true" 
        }
        
        # Multipart form data upload
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/pdf")}
            response = await client.post(url, files=files, data=data)
            
        response.raise_for_status() # Bắn Exception ngay nếu status != 2xx
        
        data = response.json()
        job_id = data.get("id")
        
        if not job_id:
            raise ValueError("Payload trả về không chứa Job ID hợp lệ.")
            
        logger.info(f"Upload thành công. Job ID: {job_id}")
        return job_id

    async def _wait_for_job_completion(self, client: httpx.AsyncClient, job_id: str):
        url = f"{self.base_url}/job/{job_id}"
        
        max_retries = 15
        base_delay = 2.0  # Bắt đầu chờ 2 giây
        max_delay = 10.0  # Chờ tối đa 10 giây mỗi lần
        
        for attempt in range(max_retries):
            response = await client.get(url)
            response.raise_for_status()
            
            status = response.json().get("status", "UNKNOWN")
            logger.debug(f"Job [{job_id}] - Lần thử [{attempt + 1}] - Status: {status}")
            
            if status == "SUCCESS":
                logger.info(f"Job [{job_id}] đã hoàn tất.")
                return
            elif status == "ERROR":
                raise RuntimeError(f"LlamaParse xử lý thất bại cho Job ID: {job_id}")
            
            # Thuật toán Exponential Backoff: Tăng dần thời gian chờ để tránh spam API
            delay = min(base_delay * (1.5 ** attempt), max_delay)
            
            # Hàm này trả lại quyền điều khiển cho Event Loop, KHÔNG block thread
            await asyncio.sleep(delay)
            
        raise TimeoutError(f"Vượt quá số lần thử. Job [{job_id}] bị treo.")

    async def _fetch_markdown_result(self, client: httpx.AsyncClient, job_id: str) -> str:
        url = f"{self.base_url}/job/{job_id}/result/markdown"
        response = await client.get(url)
        response.raise_for_status()
        
        logger.info(f"Đã lấy thành công Markdown từ Job [{job_id}]")
        # API trả về một JSON object có chứa trường "markdown"
        try:
            data = response.json()
            return data.get("markdown", response.text)
        except Exception:
            return response.text

# --- Cách gọi trong một ứng dụng Async ---
async def main():
    api_key = "llx-UPOmlt8qMiAxlyVJaiI0Sq4joeQHXuGRplrZwXbDHjqBqJjT"
    client = LlamaParseAsyncClient(api_key=api_key)
    
    try:
        folder_path = Path("/mnt/d/Project/Chatbot/Data/Input/General/")
        output_dir = Path("/mnt/d/Project/Chatbot/clean_markdown/API_Llama")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Chỉ chọn đúng 2 file PDF cụ thể theo yêu cầu
        pdf_files = [
            folder_path / "Tài liệu phân bổ quỹ học bổng.pdf",
            folder_path / "VayVon.pdf"
        ]
        
        # 2. Tạo một hàm nhỏ để xử lý từng file
        async def process_file(file):
            try:
                markdown_content = await client.parse_pdf_to_markdown(str(file))
                output_file = output_dir / f"{file.stem}.md"
                output_file.write_text(markdown_content, encoding="utf-8")
                print(f"Đã lưu thành công: {output_file.name}")
            except Exception as e:
                print(f"Lỗi khi xử lý file {file.name}: {e}")

        # 3. Xử lý đồng thời nhiều file cùng lúc cực kỳ hiệu quả nhờ AsyncIO
        print(f"Bắt đầu xử lý đồng thời {len(pdf_files)} file...")
        tasks = [process_file(file) for file in pdf_files]
        await asyncio.gather(*tasks)
        
        print("\n=== ĐÃ HOÀN THÀNH TẤT CẢ ===")

    except Exception as e:
        logger.error(f"Tiến trình bị hủy do lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(main())