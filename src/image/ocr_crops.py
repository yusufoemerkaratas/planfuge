import logging
import shutil
from pathlib import Path
from PIL import Image

# Setup logger
logger = logging.getLogger(__name__)

# Try to import pytesseract dynamically
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def check_tesseract_availability() -> bool:
    """Check if the pytesseract library is available and the tesseract binary is in PATH."""
    if not PYTESSERACT_AVAILABLE:
        return False
    return shutil.which("tesseract") is not None


def run_ocr_on_crops(crops_metadata: list, psm: int = 6) -> list:
    """
    Run OCR on a list of crop image metadata dictionaries.
    
    Conforms to the schema and falls back gracefully if Tesseract or language packs are missing.
    """
    results = []
    
    # Pre-check tesseract binary presence
    tesseract_in_path = shutil.which("tesseract") is not None
    tesseract_available = PYTESSERACT_AVAILABLE and tesseract_in_path
    
    for item in crops_metadata:
        region_id = item.get("region_id")
        crop_path = item.get("crop_path")
        
        result = {
            "region_id": region_id,
            "crop_path": crop_path,
            "ocr_text": "",
            "ocr_available": False,
            "requested_lang": "deu+eng",
            "used_lang": None,
            "warning": None
        }
        
        if not tesseract_available:
            if not PYTESSERACT_AVAILABLE:
                warning_msg = "pytesseract Python library is not installed"
            else:
                warning_msg = "Tesseract binary not found in PATH"
            logger.warning(f"OCR skipped for {region_id}: {warning_msg}")
            result["warning"] = warning_msg
            results.append(result)
            continue
            
        # Ensure the crop path exists
        if not crop_path or not Path(crop_path).exists():
            warning_msg = f"Crop path {crop_path} does not exist"
            logger.warning(warning_msg)
            result["warning"] = warning_msg
            results.append(result)
            continue
            
        try:
            # Load image and convert to grayscale (L mode)
            with Image.open(crop_path) as img:
                img_gray = img.convert("L")
                
                # Attempt OCR with fallback sequence
                ocr_text = ""
                used_lang = None
                warning = None
                
                # 1. Try deu+eng
                try:
                    config_str = f"--psm {psm}"
                    ocr_text = pytesseract.image_to_string(
                        img_gray, 
                        lang="deu+eng", 
                        config=config_str, 
                        timeout=5
                    )
                    used_lang = "deu+eng"
                except Exception as e:
                    logger.warning(f"OCR with deu+eng failed for {region_id}, trying eng: {e}")
                    # 2. Try eng
                    try:
                        ocr_text = pytesseract.image_to_string(
                            img_gray, 
                            lang="eng", 
                            config=config_str, 
                            timeout=5
                        )
                        used_lang = "eng"
                        warning = f"deu+eng failed: {str(e)}"
                    except Exception as e2:
                        logger.warning(f"OCR with eng failed for {region_id}, trying default: {e2}")
                        # 3. Try default language (no lang parameter)
                        try:
                            ocr_text = pytesseract.image_to_string(
                                img_gray, 
                                config=config_str, 
                                timeout=5
                            )
                            used_lang = None
                            warning = f"deu+eng and eng failed: {str(e2)}"
                        except Exception as e3:
                            logger.error(f"OCR completely failed for {region_id}: {e3}")
                            used_lang = None
                            warning = f"OCR completely failed: {str(e3)}"
                            ocr_text = ""
                
                # Format OCR text: strip leading/trailing whitespace
                ocr_text_clean = ocr_text.strip() if ocr_text else ""
                
                # Populate result
                result["ocr_text"] = ocr_text_clean
                # ocr_available is true if pytesseract successfully executed OCR (even if no text was found)
                # unless it raised an exception for all attempts.
                result["ocr_available"] = (used_lang is not None or "OCR completely failed" not in (warning or ""))
                result["used_lang"] = used_lang
                result["warning"] = warning
                
        except Exception as img_err:
            logger.error(f"Failed to process image {crop_path}: {img_err}")
            result["warning"] = f"Failed to process image: {str(img_err)}"
            
        results.append(result)
        
    return results
