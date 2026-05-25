import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createPost } from '../api';
import { HiArrowLeft } from 'react-icons/hi2';
import toast from 'react-hot-toast';

const EMOJIS = ['✨', '🔥', '💡', '🚀', '💀', '🎯', '💎', '🌈', '🎵', '📸', '🧠', '💬', '❤️', '⚡', '🌊', '🍕'];

function CreatePost() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [author, setAuthor] = useState('');
  const [emoji, setEmoji] = useState('✨');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required, bestie! 😤');
      return;
    }

    setSubmitting(true);
    try {
      const res = await createPost({
        title: title.trim(),
        content: content.trim(),
        author: author.trim() || 'Anonymous',
        emoji,
      });
      toast.success('Post created! You ate that 🔥');
      navigate(`/post/${res.data.id}`);
    } catch (err) {
      toast.error('Failed to create post 😢');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="form-page">
      <Link to="/" className="post-detail-back">
        <HiArrowLeft size={16} /> Back to feed
      </Link>
      <h1>Create a New Post ✍️</h1>

      <form className="form-card" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Pick a vibe</label>
          <div className="emoji-picker">
            {EMOJIS.map((e) => (
              <button
                key={e}
                type="button"
                className={`emoji-option ${emoji === e ? 'selected' : ''}`}
                onClick={() => setEmoji(e)}
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            type="text"
            placeholder="Something fire goes here..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={255}
          />
        </div>

        <div className="form-group">
          <label htmlFor="author">Author</label>
          <input
            id="author"
            type="text"
            placeholder="Your name (or stay anonymous, we don't judge)"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            maxLength={100}
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">Content</label>
          <textarea
            id="content"
            placeholder="Spill your thoughts... no character limit, go off 💅"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Posting...' : 'Post it 🚀'}
          </button>
          <Link to="/" className="btn btn-secondary">
            Nvm, cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

export default CreatePost;
