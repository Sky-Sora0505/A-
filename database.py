"""
Simple Key-Value Database using Immutable Binary Tree
Based on DBDB (Dog Bed Database) concepts
"""
import json
import os
import pickle


class BinaryNode:
    """A node in the binary tree"""
    def __init__(self, key, value, left=None, right=None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right


class BinaryTree:
    """Immutable binary tree for key-value storage"""
    def __init__(self, root=None):
        self.root = root
    
    def get(self, key):
        """Get value by key"""
        return self._get(self.root, key)
    
    def _get(self, node, key):
        if node is None:
            raise KeyError(f"Key not found: {key}")
        if key < node.key:
            return self._get(node.left, key)
        elif key > node.key:
            return self._get(node.right, key)
        else:
            return node.value
    
    def set(self, key, value):
        """Set value for key, returns new tree"""
        new_root = self._insert(self.root, key, value)
        return BinaryTree(new_root)
    
    def _insert(self, node, key, value):
        if node is None:
            return BinaryNode(key, value)
        
        if key < node.key:
            new_left = self._insert(node.left, key, value)
            return BinaryNode(node.key, node.value, new_left, node.right)
        elif key > node.key:
            new_right = self._insert(node.right, key, value)
            return BinaryNode(node.key, node.value, node.left, new_right)
        else:
            return BinaryNode(key, value, node.left, node.right)
    
    def delete(self, key):
        """Delete key, returns new tree"""
        new_root = self._delete(self.root, key)
        return BinaryTree(new_root)
    
    def _delete(self, node, key):
        if node is None:
            raise KeyError(f"Key not found: {key}")
        
        if key < node.key:
            new_left = self._delete(node.left, key)
            return BinaryNode(node.key, node.value, new_left, node.right)
        elif key > node.key:
            new_right = self._delete(node.right, key)
            return BinaryNode(node.key, node.value, node.left, new_right)
        else:
            # Node to delete found
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Node has two children, find successor
                successor = self._find_min(node.right)
                new_right = self._delete(node.right, successor.key)
                return BinaryNode(successor.key, successor.value, node.left, new_right)
    
    def _find_min(self, node):
        while node.left is not None:
            node = node.left
        return node
    
    def all_items(self):
        """Get all key-value pairs"""
        items = []
        self._traverse(self.root, items)
        return items
    
    def _traverse(self, node, items):
        if node is not None:
            self._traverse(node.left, items)
            items.append((node.key, node.value))
            self._traverse(node.right, items)


class Database:
    """Persistent key-value database"""
    def __init__(self, filepath):
        self.filepath = filepath
        self.tree = BinaryTree()
        self._load()
    
    def _load(self):
        """Load database from disk"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'rb') as f:
                    data = pickle.load(f)
                    self.tree = BinaryTree(data)
            except:
                pass
    
    def _save(self):
        """Save database to disk"""
        with open(self.filepath, 'wb') as f:
            pickle.dump(self.tree.root, f)
    
    def get(self, key):
        """Get value by key"""
        return self.tree.get(key)
    
    def set(self, key, value):
        """Set value for key"""
        self.tree = self.tree.set(key, value)
        self._save()
    
    def delete(self, key):
        """Delete key"""
        self.tree = self.tree.delete(key)
        self._save()
    
    def all_items(self):
        """Get all items"""
        return self.tree.all_items()
    
    def keys(self):
        """Get all keys"""
        return [k for k, v in self.tree.all_items()]
    
    def values(self):
        """Get all values"""
        return [v for k, v in self.tree.all_items()]
