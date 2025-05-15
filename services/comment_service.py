from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.schemas import CommentCreate
from database.models import Comment as CommentModel, Course, User

def create_comment(db: Session, comment_data: CommentCreate) -> CommentModel:
    """
    Create a new comment with validation for:
    - User must exist
    - Course must exist if course_id is provided
    
    Args:
        db: Database session
        comment_data: Comment creation data
        
    Returns:
        The created comment
        
    Raises:
        HTTPException: If validation fails
    """
    # Check if user exists
    user = db.query(User).filter(User.id == comment_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {comment_data.user_id} not found"
        )
    
    # Check if course exists if course_id is provided
    if comment_data.course_id is not None:
        course = db.query(Course).filter(Course.id_course == comment_data.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {comment_data.course_id} not found"
            )
    
    # Create the comment (quiz_id will be None if not provided)
    db_comment = CommentModel(
        user_id=comment_data.user_id,
        quiz_id=None,  # This can be None
        course_id=comment_data.course_id,  # This can be None
        comment_text=comment_data.comment_text,
        likes=min(max(comment_data.likes, 0), 5)  # Ensure likes stays within 0-5 range
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

def get_comment_by_id(db: Session, comment_id: int) -> CommentModel:
    """
    Get a single comment by its ID
    
    Args:
        db: Database session
        comment_id: ID of the comment to retrieve
        
    Returns:
        The comment if found
        
    Raises:
        HTTPException: If comment is not found
    """
    comment = db.query(CommentModel).filter(CommentModel.id_comment == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found"
        )
    return comment

def get_comments_by_course_id(db: Session, course_id: int) -> List[CommentModel]:
    """
    Get all comments for a specific course
    
    Args:
        db: Database session
        course_id: ID of the course to get comments for
        skip: Number of comments to skip (for pagination)
        limit: Maximum number of comments to return
        
    Returns:
        List of comments for the course
    """
    # First verify course exists
    course = db.query(Course).filter(Course.id_course == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    return db.query(CommentModel)\
             .filter(CommentModel.course_id == course_id)\
             .all()