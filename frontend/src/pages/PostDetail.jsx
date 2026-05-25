import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getPost, deletePost } from '../api';
import { formatDistanceToNow } from 'date-fns';
import { HiArrowLeft, HiPencil, HiTrash } from 'react-icons/hi2';
import CommentSection from '../components/CommentSection';
import ConfirmModal from '../components/ConfirmModal';
import toast from 'react-hot-toast';

function PostDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const res = await getPost(id);
      setPost(res.data);
    } catch (err) {
      console.error('Failed to fetch post:', err);
      toast.error('Post not found 😢');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await deletePost(id);
      toast.success('Post deleted! Gone like my motivation 🗑️');
      navigate('/');
    } catch (err) {
      toast.error('Failed to delete post');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner" />
      </div>
    );
  }

  if (!post) return null;

  const timeAgo = formatDistanceToNow(new Date(post.created_at), { addSuffix: true });
  const wasEdited = post.updated_at !== post.created_at;

  return (
    <div className="post-detail">
      <div className="post-detail-header">
        <Link to="/" className="post-detail-back">
          <HiArrowLeft size={16} /> Back to feed
        </Link>

        <div className="post-detail-emoji">{post.emoji || '✨'}</div>
        <h1 className="post-detail-title">{post.title}</h1>

        <div className="post-detail-meta">
          <span className="author-chip">👤 {post.author}</span>
          <span>{timeAgo}</span>
          {wasEdited && <span style={{ color: 'var(--accent-purple)' }}>(edited)</span>}
        </div>

        <div className="post-detail-actions">
          <Link to={`/edit/${post.id}`} className="btn btn-secondary btn-sm">
            <HiPencil size={16} /> Edit
          </Link>
          <button className="btn btn-danger btn-sm" onClick={() => setShowDeleteModal(true)}>
            <HiTrash size={16} /> Delete
          </button>
        </div>
      </div>

      <div className="post-detail-content">{post.content}</div>

      <CommentSection
        postId={post.id}
        comments={post.comments || []}
        onUpdate={fetchPost}
      />

      {showDeleteModal && (
        <ConfirmModal
          title="Delete this post?"
          message="This is permanent, no take-backs bestie. All comments will be gone too."
          emoji="💀"
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteModal(false)}
        />
      )}
    </div>
  );
}

export default PostDetail;
