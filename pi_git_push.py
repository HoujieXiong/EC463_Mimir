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
