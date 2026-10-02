
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from tasks.models import Task

######## CREATING TASK #############
class TaskAPITest(APITestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )

        # Generate an authentication token
        self.token = Token.objects.create(user=self.user)

        # Authenticate the API test client
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )

        self.task_url = '/tasks-viewset/'

    def test_create_task(self):
        # Arrange: prepare task data
        data = {
            'title': 'Learn Django testing',
            'description': 'Practice automated API tests',
            'completed': False
        }

        # Act: send POST request
        response = self.client.post(
            self.task_url,
            data,
            format='json'
        )
        print(response.data)

        # Assert: verify the response
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['title'],
            'Learn Django testing'
        )

        # Verify that the task was assigned to the authenticated user
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.owner, self.user)




##################### Test invalid task creation ####################

    def test_create_task_with_short_title(self):
        data = {
            'title': 'API',
            'description': 'Testing invalid title',
            'completed': False
        }

        response = self.client.post(
            self.task_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn('title', response.data)


##################### Test user isolation ####################

    def test_user_sees_only_their_own_tasks(self):
        # Create another user
        other_user = User.objects.create_user(
            username='anotheruser',
            password='AnotherPass123!'
        )

        # Create a task belonging to that user
        Task.objects.create(
            title='Other users task',
            description='This belongs to another user',
            completed=False,
            owner=other_user
        )

        # Request tasks as the currently authenticated user
        response = self.client.get(self.task_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get task results from the paginated response
        task_results = response.data['results']

        # Ensure no task belonging to another user is returned
        for task in task_results:
            self.assertNotEqual(task['title'], 'Other users task')


##################### Test task updates ##################

    def test_update_task(self):
        # Create a task owned by the authenticated user
        task = Task.objects.create(
            title='Learn Python',
            description='Practice Python basics',
            completed=False,
            owner=self.user
        )

        # Prepare updated data
        data = {
            'title': 'Learn Django',
            'description': 'Practice Django REST Framework',
            'completed': True
        }

        # Send a PUT request to update the task
        response = self.client.put(
            f'{self.task_url}{task.id}/',
            data,
            format='json'
        )

        # Verify the response
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(response.data['title'], 'Learn Django')
        self.assertTrue(response.data['completed'])

        # Verify the database was updated
        task.refresh_from_db()
        self.assertEqual(task.title, 'Learn Django')
        self.assertTrue(task.completed)


################################# Test task deletion ###################

    def test_delete_task(self):
        # Create a task owned by the authenticated user
        task = Task.objects.create(
            title='Delete this task',
            description='This task will be deleted',
            completed=False,
            owner=self.user
        )

        # Send DELETE request
        response = self.client.delete(
            f'{self.task_url}{task.id}/'
        )

        # Verify the API response
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        # Verify the task no longer exists in the database
        self.assertFalse(
            Task.objects.filter(id=task.id).exists()
        )

################## Test unauthenticated access ##################

    
    def test_unauthenticated_user_cannot_access_tasks(self):
        # Remove authentication credentials
        self.client.credentials()

        # Try to fetch tasks without logging in
        response = self.client.get(self.task_url)

        # Verify that access is denied
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


################ Test task ownership permissions ##############

    def test_user_cannot_delete_another_users_task(self):
        # Create another user
        other_user = User.objects.create_user(
            username='anotheruser',
            password='AnotherPass123!'
        )

        # Create a task owned by the other user
        other_task = Task.objects.create(
            title='Private task',
            description='This belongs to another user',
            completed=False,
            owner=other_user
        )

        # Try to delete the other user's task
        response = self.client.delete(
            f'{self.task_url}{other_task.id}/'
        )

        # The task should not be accessible to this user
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # Verify the task still exists
        self.assertTrue(
            Task.objects.filter(id=other_task.id).exists()
        )




################# Test filtering, searching, ordering, and pagination ###############
    def test_partial_update_task(self):
        task = Task.objects.create(
            title='Learn Python',
            description='Practice Python basics',
            completed=False,
            owner=self.user
        )

        response = self.client.patch(
            f'{self.task_url}{task.id}/',
            {'title': 'Learn Django'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task.refresh_from_db()
        self.assertEqual(task.title, 'Learn Django')
        self.assertEqual(task.description, 'Practice Python basics')
        self.assertFalse(task.completed)

    def test_filter_tasks_by_completed_status(self):
        Task.objects.create(
            title='Completed task',
            description='This task is completed',
            completed=True,
            owner=self.user
        )
        Task.objects.create(
            title='Pending task',
            description='This task is still pending',
            completed=False,
            owner=self.user
        )

        response = self.client.get(
            self.task_url,
            {'completed': 'true'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        self.assertTrue(len(results) > 0)

        for task in results:
            self.assertTrue(task['completed'])

    def test_search_tasks_by_title(self):
        Task.objects.create(
            title='Learn Django REST',
            description='Study APIs',
            completed=False,
            owner=self.user
        )
        Task.objects.create(
            title='Practice Java',
            description='Study programming',
            completed=False,
            owner=self.user
        )

        response = self.client.get(
            self.task_url,
            {'search': 'Django'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        self.assertTrue(len(results) > 0)

        for task in results:
            self.assertIn('Django', task['title'])

    def test_order_tasks_by_title(self):
        Task.objects.create(
            title='Zebra task',
            description='Last alphabetically',
            completed=False,
            owner=self.user
        )
        Task.objects.create(
            title='Apple task',
            description='First alphabetically',
            completed=False,
            owner=self.user
        )

        response = self.client.get(
            self.task_url,
            {'ordering': 'title'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [task['title'] for task in response.data['results']]
        self.assertEqual(titles, sorted(titles))

    def test_task_list_pagination(self):
        for number in range(5):
            Task.objects.create(
                title=f'Test task {number}',
                description='Task for pagination testing',
                completed=False,
                owner=self.user
            )

        response = self.client.get(self.task_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 3)
        self.assertIsNotNone(response.data['next'])

    def test_register_user(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'registrationtest',
                'password': 'StrongPass123!'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertTrue(
            User.objects.filter(username='registrationtest').exists()
        )

        registered_user = User.objects.get(username='registrationtest')
        self.assertTrue(
            registered_user.check_password('StrongPass123!')
        )

    def test_login_with_valid_credentials(self):
        self.client.credentials()

        response = self.client.post(
            '/api/login/',
            {
                'username': 'testuser',
                'password': 'TestPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_with_invalid_credentials(self):
        self.client.credentials()

        response = self.client.post(
            '/api/login/',
            {
                'username': 'testuser',
                'password': 'WrongPassword!'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_user_cannot_update_another_users_task(self):
        other_user = User.objects.create_user(
            username='updateowner',
            password='AnotherPass123!'
        )

        other_task = Task.objects.create(
            title='Private task',
            description='Owned by another user',
            completed=False,
            owner=other_user
        )

        response = self.client.patch(
            f'{self.task_url}{other_task.id}/',
            {'title': 'Changed by another user'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        other_task.refresh_from_db()
        self.assertEqual(other_task.title, 'Private task')

    def test_register_duplicate_username(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'testuser',
                'password': 'AnotherPass123!'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )