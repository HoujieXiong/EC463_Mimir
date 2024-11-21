import subprocess

repo_path=""
def git_pull(repo_path):
    """
    Performs a `git pull` operation in the specified repository path.
    
    Args:
        repo_path (str): The local path of the Git repository.
    
    Returns:
        str: The output of the `git pull` command.
    """
    try:
        # Change the current working directory to the repo path
        result = subprocess.run(
            ["git", "-C", repo_path, "pull"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print("Git pull successful!")
        else:
            print("Git pull failed!")
        return result.stdout + result.stderr
    except Exception as e:
        print(f"Error running git pull: {e}")
        return str(e)

git_pull(repo_path)