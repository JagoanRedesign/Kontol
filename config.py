from dotenv import load_dotenv
import os


load_dotenv()

api_id = int(os.getenv("API_ID", ""))
api_hash = os.getenv("API_HASH", "")

prefix = os.getenv("PREFIX", "! . * ^").split()
group_blacklist = [
    -1001883961446,
    -1001847953700,
    -1001473548283,
    -1001777794636,
    -1001109837870
]
