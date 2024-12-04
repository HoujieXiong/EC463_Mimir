import git

# Path to your local Git repository
repo_path = "/home/Visual_AI/Desktop/EC463_Mimir"

# Open the repository
repo = git.Repo(repo_path)

# Stage all changes (equivalent to `git add .`)
repo.git.add(A=True)

# Commit the changes
commit_message = "Auto Update"
repo.index.commit(commit_message)

# Push the changes to the remote repository
origin = repo.remote(name="origin")
origin.push()

print("Changes pushed successfully.")


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
            return 1
        else:
            print("Git pull failed!")
            return 0
    except Exception as e:
        print(f"Error running git pull: {e}")
        return str(e)

