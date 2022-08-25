variable "git_repo_url" {
  type        = string
  description = "The URL of the current git repository. This variable is supplied automatically when ML resource config is updated through automation."
}

variable "github_repo" {
  type        = string
  description = "The owner and repo name of the current GitHub repository, in the format <owner>/<repo-name>. This variable is supplied automatically when ML resource config is updated through automation."
}

variable "github_actions_token" {
  type        = string
  description = "GitHub OAuth token with write permissions on the current repo, to use to trigger CD workflows defined using GitHub Actions in the current repo"
}
