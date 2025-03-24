from collections import deque

class Queue:
    def __init__(self):
        """Initializes an empty queue using deque for efficient FIFO operations [[8]]."""
        self.items = deque()  # Double-ended queue for O(1) append/popleft

    def is_empty(self):
        """Checks if the queue is empty."""
        return len(self.items) == 0

    def enqueue(self, item):
        """
        Adds an item to the end of the queue (O(1) time complexity).
        Args:
            item (PullRequest): PR to add to the queue.
        """
        self.items.append(item)

    def dequeue(self):
        """
        Removes and returns the front item from the queue (O(1) time complexity).
        Returns:
            PullRequest: The oldest PR in the queue.
        Raises:
            IndexError: If the queue is empty.
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self.items.popleft()

    def peek(self):
        """
        Returns the front item without removing it.
        Returns:
            PullRequest: The oldest PR in the queue.
        Raises:
            IndexError: If the queue is empty.
        """
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self.items[0]

    def clear(self):
        """Removes all items from the queue (O(1) time complexity)."""
        self.items.clear()

    def __len__(self):
        """Returns the number of PRs in the queue."""
        return len(self.items)

    def get_all(self):
        """Returns a list of all PRs in the queue (for status display)."""
        return list(self.items)
    
    def find_pr_by_id(self, pr_id):
        """Returns PRs if the ID matches the seach (for status display)."""
        for pr in self.items:
            if pr.id == pr_id:
                return pr
        return None