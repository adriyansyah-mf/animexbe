# 📚 Bookmark Feature API Guide

## Overview
The bookmark feature allows users to save their favorite anime for easy access later. Users can add, remove, list, and check bookmark status for any anime in the system.

## 🔐 Authentication Required
All bookmark endpoints require user authentication via JWT token. First, register and login to get your access token.

## 📋 API Endpoints

### 1. 👤 User Registration & Login

#### Register New User
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/user/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### User Login
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/user/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com", 
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "bearer"
}
```

### 2. ⭐ Bookmark Operations

#### Add Bookmark
Save an anime to your bookmarks:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/user/bookmarks' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "content_id": 123,
    "url": "https://example.com/anime/attack-on-titan"
  }'
```

**Response:**
```json
{
  "message": "Bookmark added successfully",
  "bookmark_id": 456,
  "content_id": 123
}
```

#### Remove Bookmark
Remove an anime from your bookmarks:

```bash
curl -X 'DELETE' \
  'http://127.0.0.1:8000/user/bookmarks/123' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

**Response:**
```json
{
  "message": "Bookmark removed successfully",
  "content_id": 123
}
```

#### Get All User Bookmarks
Retrieve all your bookmarked anime with full details:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/user/bookmarks' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

**Response:**
```json
[
  {
    "id": 456,
    "url": "https://example.com/anime/attack-on-titan",
    "content_id": 123,
    "created_at": 1673123456,
    "anime_title": "Attack on Titan: Final Season",
    "anime_banner": "https://example.com/banners/aot.jpg",
    "anime_status": "Completed"
  },
  {
    "id": 457,
    "url": "https://example.com/anime/demon-slayer",
    "content_id": 124,
    "created_at": 1673123789,
    "anime_title": "Demon Slayer: Kimetsu no Yaiba",
    "anime_banner": "https://example.com/banners/ds.jpg", 
    "anime_status": "Ongoing"
  }
]
```

#### Check Bookmark Status
Check if a specific anime is in your bookmarks:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/user/bookmarks/check/123' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

**Response:**
```json
{
  "content_id": 123,
  "is_bookmarked": true
}
```

### 3. 🎬 Browse Anime (No Auth Required)

#### List All Anime
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/user/list-anime?page=1&per_page=10&status=Ongoing'
```

#### Get Anime Details
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/user/anime/123'
```

## 🎯 Use Cases

### Frontend Integration Example

```javascript
// Add bookmark functionality
async function toggleBookmark(animeId, animeUrl) {
  const token = localStorage.getItem('authToken');
  
  // Check current status
  const checkResponse = await fetch(`/user/bookmarks/check/${animeId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const { is_bookmarked } = await checkResponse.json();
  
  if (is_bookmarked) {
    // Remove bookmark
    await fetch(`/user/bookmarks/${animeId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    showMessage('Bookmark removed!');
  } else {
    // Add bookmark
    await fetch('/user/bookmarks', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content_id: animeId,
        url: animeUrl
      })
    });
    showMessage('Bookmark added!');
  }
}

// Load user's bookmarks
async function loadBookmarks() {
  const token = localStorage.getItem('authToken');
  const response = await fetch('/user/bookmarks', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const bookmarks = await response.json();
  
  displayBookmarks(bookmarks);
}
```

## 🛡️ Security Features

- **JWT Authentication**: All bookmark operations require valid user authentication
- **User Isolation**: Users can only access their own bookmarks
- **Duplicate Prevention**: System prevents duplicate bookmarks for the same anime
- **Input Validation**: All inputs are validated using Pydantic schemas

## ✨ Advanced Features

- **Rich Bookmark Data**: Bookmarks include anime title, banner, and status
- **Chronological Ordering**: Bookmarks are returned with newest first
- **Efficient Queries**: Optimized database queries with proper joins
- **Error Handling**: Comprehensive error responses with helpful messages

## 🎨 Status Codes

- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid or missing token)
- `404`: Not Found (user or bookmark not found)
- `500`: Internal Server Error

## 🚀 Next Steps

1. **Start your API server**: `docker-compose up`
2. **Register a user account**
3. **Login to get your JWT token**
4. **Start bookmarking your favorite anime!**

Happy bookmarking! 🎉 