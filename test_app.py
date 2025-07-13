import unittest
import json
from app import app, init_db  # Adjust import to your actual filename

class TodoApiTestCase(unittest.TestCase):
    def setUp(self):
        # Initialize DB & test client before each test
        init_db()
        self.client = app.test_client()
    
    def test_create_task_success(self):
        response = self.client.post('/tasks', json={"title": "Test Task"})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['title'], "Test Task")
        self.assertFalse(data['completed'])
    
    def test_create_task_missing_title(self):
        response = self.client.post('/tasks', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_create_task_empty_title(self):
        response = self.client.post('/tasks', json={"title": "   "})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_get_tasks(self):
        # First create a task
        self.client.post('/tasks', json={"title": "Task 1"})
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(task['title'] == 'Task 1' for task in data))
    
    def test_update_task_title_and_completed(self):
        # Create a task
        post_resp = self.client.post('/tasks', json={"title": "Old Title"})
        task_id = post_resp.get_json()['id']
        
        # Update title and completed
        patch_resp = self.client.patch(f'/tasks/{task_id}', json={"title": "New Title", "completed": True})
        self.assertEqual(patch_resp.status_code, 200)
        data = patch_resp.get_json()
        self.assertEqual(data['title'], "New Title")
        self.assertTrue(data['completed'])
    
    def test_update_task_invalid_completed(self):
        post_resp = self.client.post('/tasks', json={"title": "Task"})
        task_id = post_resp.get_json()['id']
        patch_resp = self.client.patch(f'/tasks/{task_id}', json={"completed": "not_bool"})
        self.assertEqual(patch_resp.status_code, 400)
        data = patch_resp.get_json()
        self.assertIn('error', data)
    
    def test_delete_task(self):
        post_resp = self.client.post('/tasks', json={"title": "To delete"})
        task_id = post_resp.get_json()['id']
        delete_resp = self.client.delete(f'/tasks/{task_id}')
        self.assertEqual(delete_resp.status_code, 200)
        data = delete_resp.get_json()
        self.assertIn('message', data)
    
    def test_delete_task_not_found(self):
        delete_resp = self.client.delete('/tasks/999999')  # unlikely id
        self.assertEqual(delete_resp.status_code, 404)
        data = delete_resp.get_json()
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
