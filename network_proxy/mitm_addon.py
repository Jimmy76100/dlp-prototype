import sys
import os
import tempfile
import traceback
from mitmproxy import http

# --- Add the main project folder to Python's path ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- --- --- --- --- --- --- --- --- --- --- --- --- ---

try:
    from detector.extractor import extract_text_from_file
    from detector.detectors import find_patterns
except ImportError:
    print("FATAL: Could not import detector modules. Make sure the path is correct.")
    sys.exit(1)


class DLPAddon:
    
    def request(self, flow: http.HTTPFlow) -> None:
        
        if (
            flow.request.method == "POST"
            and "multipart/form-data" in flow.request.headers.get("Content-Type", "")
        ):
            print("\n-----------------------------------------")
            print(f"[DEBUG] Inspecting POST request to {flow.request.pretty_host}...")
            
            try:
                if not flow.request.multipart_form:
                    print("[DEBUG] Request is multipart, but no .multipart_form attribute found.")
                    print("-----------------------------------------\n")
                    return

                # --- !! SIMPLIFIED LOGIC !! ---
                # We will build one giant string of all text content
                # This avoids the file tuple vs. field bytes problem
                
                full_text_content = ""
                file_found = False

                for name, value in flow.request.multipart_form.items():
                    
                    # Check if this item is a file tuple: (filename, content_bytes, content_type)
                    if isinstance(value, tuple) and len(value) == 3:
                        file_found = True
                        filename, content_bytes, content_type = value
                        print(f"[DEBUG] Found file tuple: name='{name}', filename='{filename}'")
                        
                        # Save to temp file to run textract
                        with tempfile.NamedTemporaryFile(delete=True) as tmp:
                            tmp.write(content_bytes)
                            tmp.flush()
                            full_text_content += extract_text_from_file(tmp.name) + "\n"
                    
                    # Check if this item is just a byte string (a simple field)
                    elif isinstance(value, bytes):
                        print(f"[DEBUG] Found simple field: name='{name}'")
                        # Try to decode it as text
                        try:
                            full_text_content += value.decode('utf-8', errors='ignore') + "\n"
                        except:
                            pass # Not text, ignore
                    
                    # --- !! END OF SIMPLIFIED LOGIC !! ---

                if not file_found and not full_text_content:
                    print("[DEBUG] No files or text fields found in form.")
                    print("-----------------------------------------\n")
                    return
                
                print(f"[DEBUG] Total extracted text: '{full_text_content[:150]}...'") # Print first 150 chars

                # Now, scan the *entire* combined text
                matches = find_patterns(full_text_content)
                
                if matches:
                    print(f"[DEBUG] !! DLP VIOLATION FOUND !! Matches: {matches}")
                    print(f"[DEBUG] Blocking upload.")
                    
                    flow.response = http.Response.make(
                        403,  # Forbidden
                        b"Blocked by DLP: Sensitive data detected in file upload.",
                        {"Content-Type": "text/plain"}
                    )
                    print("-----------------------------------------\n")
                    return
                else:
                    print("[DEBUG] No matches found in any part of the form.")

                print("[DEBUG] No violations found. Allowing request.")
                print("-----------------------------------------\n")

            except Exception as e:
                print("\n[DEBUG] !!!!! SCRIPT CRASHED !!!!!")
                print(f"[DEBUG] ERROR: {e}")
                print(f"[DEBUG] TRACEBACK: {traceback.format_exc()}")
                print("-----------------------------------------\n")
                flow.response = http.Response.make(
                    500, b"DLP script failed during processing."
                )

addons = [
    DLPAddon()
]
