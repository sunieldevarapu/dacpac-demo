import requests

def get_example():
    response = requests.get("https://api.github.com")
    return response.status_code

if __name__ == "__main__":
    status = get_example()
    print(f"GitHub API responded with status: {status}")
