from datetime import datetime

class PullRequest:
    def __init__(self, pr_id, source_branch, target_branch):
        """
        Represents a pull request in the queue.
        Args:
            pr_id (int): Unique identifier for the PR.
            source_branch (str): Branch containing changes.
            target_branch (str): Target branch for merging.
        """
        self.id = pr_id
        self.source = source_branch
        self.target = target_branch
        self.status = "pending"          # pending, reviewing, approved, rejected, merged
        self.commits = []                # References to associated commits
        self.files = []                  # Modified files
        self.reviewers = []              # Assigned reviewers
        self.created_at = datetime.now() # Creation timestamp
        self.merged_at = None            # Merge timestamp
        self.tags = []                   # Organizational tags
        self.title = ""
        self.description = ""
        self.author = "default_user"
        self.status = "pending"
        self.closed_at = None

    def to_dict(self):
        """Converts PR data to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'status': self.status,
            'commits': self.commits,
            'files': self.files,
            'reviewers': self.reviewers,
            'created_at': self.created_at.isoformat(),
            'merged_at': self.merged_at.isoformat() if self.merged_at else None,
            'tags': self.tags,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstructs PR from dictionary (JSON deserialization)."""
        pr = cls(data['id'], data['source'], data['target'])
        pr.status = data['status']
        pr.commits = data['commits']
        pr.files = data['files']
        pr.reviewers = data['reviewers']
        pr.created_at = datetime.fromisoformat(data['created_at'])
        pr.merged_at = datetime.fromisoformat(data['merged_at']) if data['merged_at'] else None
        pr.tags = data['tags']
        pr.title = data.get('title', '')
        pr.description = data.get('description', '')
        pr.author = data.get('author', '')
        pr.closed_at = datetime.fromisoformat(data['closed_at']) if data['closed_at'] else None
        return pr