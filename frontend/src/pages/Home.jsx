import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getPosts } from '../api';
import PostCard from '../components/PostCard';
import { HiPlus } from 'react-icons/hi';

function Home() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const res = await getPosts();
      setPosts(res.data);
    } catch (err) {
      console.error('Failed to fetch posts:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div>
      <div className="home-header">
        <h1>Welcome to Jerney 🛤️</h1>
        <p>A blog platform for the main characters. Share your thoughts, vibes, and hot takes.</p>
        <div className="vibe-tags">
          <span className="vibe-tag">✨ no cap content</span>
          <span className="vibe-tag">🔥 hot takes</span>
          <span className="vibe-tag">💎 real ones only</span>
        </div>
      </div>

      {posts.length === 0 ? (
        <div className="empty-state">
          <div className="empty-emoji">📝</div>
          <h3>No posts yet, bestie</h3>
          <p>Be the first to share your thoughts on this journey</p>
          <Link to="/create" className="btn btn-primary">
            <HiPlus size={18} />
            Write something
          </Link>
        </div>
      ) : (
        <div className="posts-grid">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Home;
