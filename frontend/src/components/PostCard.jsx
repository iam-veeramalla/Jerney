import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { HiChatBubbleLeft } from 'react-icons/hi2';

function PostCard({ post }) {
  const timeAgo = formatDistanceToNow(new Date(post.created_at), { addSuffix: true });

  return (
    <Link to={`/post/${post.id}`} className="post-card">
      <div className="post-card-header">
        <div className="post-emoji">{post.emoji || '✨'}</div>
        <div>
          <h2 className="post-card-title">{post.title}</h2>
          <div className="post-card-meta">
            <span>{post.author}</span>
            <span className="dot" />
            <span>{timeAgo}</span>
          </div>
        </div>
      </div>
      <p className="post-card-preview">{post.content}</p>
      <div className="post-card-footer">
        <div className="comment-badge">
          <HiChatBubbleLeft size={16} />
          <span>{post.comment_count || 0} comments</span>
        </div>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Read more →</span>
      </div>
    </Link>
  );
}

export default PostCard;
