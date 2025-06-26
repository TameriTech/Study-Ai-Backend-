// Global variables
let currentUser = null;
let currentGroup = null;
let socket = null;
let emojiPicker = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const baseReconnectDelay = 10000; // 1 second
let reconnectTimeoutId = null;
let isManualDisconnect = false;
let allUsers = [];
let notificationManager;
let typingUsers = {};
let lastMessageDate = null;
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Global variables for message pagination
let messagePage = 1;
const MESSAGES_PER_PAGE = 20; // Number of messages to load per batch
let isLoadingMessages = false;
let allMessagesLoaded = false;
// Add these event listeners in the init() function

// DOM Elements
const loginPanel = document.getElementById('loginPanel');
const chatInterface = document.getElementById('chatInterface');
const userOptions = document.querySelectorAll('.user-option');
const usernameDisplay = document.getElementById('usernameDisplay');
const userAvatar = document.getElementById('userAvatar');
const userStatus = document.getElementById('userStatus');
const groupList = document.getElementById('groupList');
const createGroupBtn = document.getElementById('createGroupBtn');
const groupSearch = document.getElementById('groupSearch');
const currentGroupName = document.getElementById('currentGroupName');
const groupMembers = document.getElementById('groupMembers');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const emojiBtn = document.getElementById('emojiBtn');
const emojiPickerContainer = document.getElementById('emojiPicker');
const pinnedMessages = document.querySelector('.pinned-list');
const messageActions = document.getElementById('messageActions');
const passwordModal = document.getElementById('passwordModal');
const selectedUsernameDisplay = document.getElementById('selectedUsername');
const passwordInput = document.getElementById('passwordInput');
const cancelPasswordBtn = document.getElementById('cancelPasswordBtn');
const submitPasswordBtn = document.getElementById('submitPasswordBtn');

const homeScreen = document.getElementById('homeScreen');
const main_chat = document.getElementById('main_chat');

// Notification Manager Class
class NotificationManager {
    constructor() {
        this.unreadCount = 0;
        this.notifications = [];
        this.soundEnabled = true;
        this.browsserNotificationsAllowed = false;
        this.lastNotificationTime = 0;
        this.notificationThrottle = 1000; // 1 second between notifications

        this.pushNotificationsEnabled = true;

        this.initElements();
        this.initEventListeners();
        this.checkNotificationPermission();
        this.initSounds();
    }

    initElements() {
        this.bell = document.getElementById('notification-bell');
        this.badge = document.getElementById('notification-badge');
        this.dropdown = document.getElementById('notification-dropdown');
        this.list = document.getElementById('notification-list');
        this.clearBtn = document.getElementById('notification-clear');
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'notification-toast-container';
        document.body.appendChild(this.toastContainer);

        this.refreshBtn = document.createElement('button');
    this.refreshBtn.className = 'notification-refresh-btn';
    this.refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    this.refreshBtn.title = 'Refresh notifications';
    this.dropdown.insertBefore(this.refreshBtn, this.list);
    
    this.refreshBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        loadNotifications();
    });
    }

    initEventListeners() {
        this.bell.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
            this.markAllAsRead();
        });

        this.clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.clearAllNotifications();
        });

        document.addEventListener('click', () => {
            this.dropdown.classList.remove('show');
        });

        this.dropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    initSounds() {
        this.sounds = {
            message: this.createAudioElement('/tameri_chat/static/chat/files/notif0.mp3'),
            direct: this.createAudioElement('/tameri_chat/static/chat/files/notif1.mp3'),
            system: this.createAudioElement('/tameri_chat/static/chat/files/bell.mp3'),
            error: this.createAudioElement('/tameri_chat/static/chat/files/error.mp3'),
            success: this.createAudioElement('/tameri_chat/static/chat/files/success.mp3')
        };
    }

    createAudioElement(src) {
        const audio = new Audio();
        audio.src = src;
        audio.volume = 1;
        audio.preload = 'auto';
        return audio;
    }
    toggleDropdown() {
        this.dropdown.classList.toggle('show');
    }
    notify(type, title, message, data = {}, showPush = true, addToDropdown = true) {
        const now = Date.now();
        if (now - this.lastNotificationTime < this.notificationThrottle) {
            return;
        }
        this.lastNotificationTime = now;

        const notification = {
            id: now,
            type,
            title,
            message,
            data,
            timestamp: new Date(),
            read: false
        };

        // Handle push notification
        if (showPush && this.pushNotificationsEnabled) {
            this.showBrowsserNotification(notification);
            this.playSound(type);
        }

        // Handle dropdown notification
        if (addToDropdown) {
            this.addNotificationToQueue(notification);
            this.updateUI();
        }

        // Show toast notification (optional)
        this.showToast(notification);
    }

    addNotificationToQueue(notification) {
        this.notifications.unshift(notification);
        this.unreadCount++;
        this.updateUI();
    }

    updateUI() {
        this.updateBadge();
        this.animateBell();
        this.renderNotificationList();
    }

    updateBadge() {
        this.badge.textContent = this.unreadCount > 9 ? '9+' : this.unreadCount;
        this.badge.classList.toggle('show', this.unreadCount > 0);
    }

    animateBell() {
        this.bell.classList.add('ring');
        setTimeout(() => {
            this.bell.classList.remove('ring');
        }, 1000);
    }

    renderNotificationList() {
    if (this.notifications.length === 0) {
        this.list.innerHTML = '<li class="notification-empty">No notifications yet</li>';
        return;
    }

    // Group notifications by date
    const groupedNotifications = this.groupNotificationsByDate(this.notifications);
    
    this.list.innerHTML = Object.entries(groupedNotifications).map(([date, notifications]) => `
        <div class="notification-date-group">
            <div class="notification-date-header">${date}</div>
            ${notifications.map(notif => `
                <li class="notification-item ${notif.read ? 'read' : 'unread'}" data-id="${notif.id}">
                    <div class="notification-icon ${notif.type}">
                        <i class="fas ${this.getNotificationIcon(notif.type)}"></i>
                    </div>
                    <div class="notification-content">
                        <div class="notification-title">
                            <span>${notif.title}</span>
                            <span class="notification-time">${this.formatTime(notif.timestamp)}</span>
                        </div>
                        <div class="notification-text">${notif.message}</div>
                        ${notif.data.group_name ? 
                            `<div class="notification-context">In ${notif.data.group_name}</div>` : ''}
                    </div>
                    <div class="notification-actions">
                        ${!notif.read ? `
                            <button class="mark-read-btn" title="Mark as read" data-id="${notif.id}">
                                <i class="fas fa-check"></i>
                            </button>
                        ` : ''}
                        <button class="delete-notification-btn" title="Delete" data-id="${notif.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </li>
            `).join('')}
        </div>
    `).join('');

    this.addNotificationItemEventListeners();
}

groupNotificationsByDate(notifications) {
    const groups = {};
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    notifications.forEach(notif => {
        const notifDate = new Date(notif.timestamp);
        notifDate.setHours(0, 0, 0, 0);
        
        let dateLabel;
        if (notifDate.getTime() === today.getTime()) {
            dateLabel = 'Today';
        } else if (notifDate.getTime() === yesterday.getTime()) {
            dateLabel = 'Yesterday';
        } else {
            dateLabel = notifDate.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric', 
                year: 'numeric' 
            });
        }
        
        if (!groups[dateLabel]) {
            groups[dateLabel] = [];
        }
        groups[dateLabel].push(notif);
    });
    
    return groups;
}

    getNotificationIcon(type) {
        const icons = {
            message: 'fa-comment-dots',
            direct: 'fa-user',
            system: 'fa-info-circle',
            error: 'fa-exclamation-circle',
            success: 'fa-check-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    addNotificationItemEventListeners() {
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.notification-actions')) {
                const id = parseInt(item.dataset.id);
                this.markAsRead(id);

                const notification = this.notifications.find(n => n.id === id);
                if (notification && notification.data.action) {
                    this.handleNotificationAction(notification.data.action);
                }
            }
        });
    });

    // Add event listeners for action buttons
    document.querySelectorAll('.mark-read-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            this.markAsRead(id);
        });
    });

    document.querySelectorAll('.delete-notification-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = parseInt(btn.dataset.id);
            this.deleteNotification(id);
        });
    });
}

deleteNotification(id) {
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.unreadCount = this.notifications.filter(n => !n.read).length;
    this.updateUI();
    
    // Send to server to delete
    fetch(`/notifications/${id}`, {
        method: 'DELETE'
    }).catch(e => console.error('Error deleting notification:', e));
}

    handleNotificationAction(action) {
        switch (action.type) {
            case 'navigate':
                // Handle navigation
                break;
            case 'open_group':
                this.navigateToGroup(action.groupId);
                break;
            case 'open_message':
                this.navigateToMessage(action.messageId);
                break;
            default:
                console.log('Unknown action type:', action.type);
        }
    }

    navigateToGroup(groupId) {
        const group = findGroupById(groupId);
        if (group) {
            selectGroup(group);
        }
    }

    navigateToMessage(messageId) {
        // Scroll to message in chat
        const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.scrollIntoView({ behavior: 'smooth' });
            messageElement.classList.add('highlight');
            setTimeout(() => {
                messageElement.classList.remove('highlight');
            }, 2000);
        }
    }

    markAsRead(id) {
    const notification = this.notifications.find(n => n.id === id);
    if (notification && !notification.read) {
        notification.read = true;
        this.unreadCount--;
        this.updateUI();
        
        // Send to server to mark as read
        fetch(`/notifications/mark-read`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                notification_ids: [id],
                user_id: currentUser.id
            })
        }).catch(e => console.error('Error marking notification as read:', e));
        
        // Update unread count
        updateUnreadCount();
    }
}

markAllAsRead() {
    const unreadIds = this.notifications
        .filter(n => !n.read)
        .map(n => n.id);
    
    if (unreadIds.length === 0) return;
    
    // Mark all as read locally
    this.notifications.forEach(n => n.read = true);
    this.unreadCount = 0;
    this.updateUI();
    
    // Send to server to mark all as read
    fetch(`/notifications/mark-read`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            notification_ids: unreadIds,
            user_id: currentUser.id
        })
    }).then(() => {
        updateUnreadCount();
    }).catch(e => console.error('Error marking notifications as read:', e));
}

    clearAllNotifications() {
        this.notifications = [];
        this.unreadCount = 0;
        this.updateUI();
    }

    playSound(type) {
        if (!this.soundEnabled || !this.sounds[type]) return;

        try {
            const audio = this.sounds[type].cloneNode();
            audio.volume = 0.1;
            audio.play().catch(e => console.log("Audio playback failed:", e));
        } catch (e) {
            console.error("Error playing sound:", e);
        }
    }

    showToast(notification) {
        const toast = document.createElement('div');
        toast.className = `notification-toast show ${notification.type}`;
        toast.innerHTML = `
      <div class="notification-toast-icon">
        <i class="fas ${this.getNotificationIcon(notification.type)}"></i>
      </div>
      <div class="notification-toast-content">
        <div class="notification-toast-title">${notification.title}</div>
        <div class="notification-toast-text">${notification.message}</div>
      </div>
      <button class="notification-toast-close">
        <i class="fas fa-times"></i>
      </button>
    `;

        this.toastContainer.appendChild(toast);

        toast.querySelector('.notification-toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });

        setTimeout(() => {
            this.removeToast(toast);
        }, 5000);
    }

    removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    showBrowsserNotification(notification) {
        if (!this.browsserNotificationsAllowed || document.hasFocus()) return;

        const title = notification.title;
        const options = {
            body: notification.message,
            icon: '/tameri_chat/static/chat/files/logo.png',
            tag: 'chat-notification',
            data: notification.data
        };

        try {
            new Notification(title, options);
        } catch (e) {
            console.error("Browsser notification error:", e);
        }
    }

    checkNotificationPermission() {
        if ('Notification' in window) {
            this.browsserNotificationsAllowed = Notification.permission === 'granted';
        }
    }

    requestNotificationPermission() {
        if ('Notification' in window && !this.browsserNotificationsAllowed) {
            Notification.requestPermission().then(permission => {
                this.browsserNotificationsAllowed = permission === 'granted';
            });
        }
    }

    formatTime(date) {
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}

// Add these functions BEFORE the init() function
function startRecording() {
    if (isRecording) return;
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            isRecording = true;
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);
            
            // Show local indicator
            document.getElementById('recordingIndicator').style.display = 'flex';
            document.getElementById('recordBtn').style.display = 'none';
            
            // Notify group members
            sendRecordingStatus(true);
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                sendVoiceMessage(audioBlob);
                // Notify group members recording stopped
                sendRecordingStatus(false);
            };
            
            mediaRecorder.start();
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
            notificationManager.notify('error', 'Microphone Error', 'Could not access microphone');
        });
}

function stopRecording() {
    if (!isRecording) return;
    
    isRecording = false;
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    
    document.getElementById('recordingIndicator').style.display = 'none';
    document.getElementById('recordBtn').style.display = 'flex';
    
    // Notify group members recording stopped
    sendRecordingStatus(false);
}

function sendVoiceMessage(audioBlob) {
    if (!currentGroup) {
        notificationManager.notify('error', 'Error', 'No group selected');
        return;
    }
    
    // Create a unique filename
    const filename = `voice_${Date.now()}.mp3`;
    
    const reader = new FileReader();
    reader.onload = () => {
        const audioData = reader.result;
        
        const message = {
            type: 'voice_message',
            data: {
                group_id: currentGroup.id,
                audio: audioData,
                duration: Math.round(audioBlob.size / 6000), // Rough estimate
                sender_id: currentUser.id,
                created_at: new Date().toISOString()
            }
        };
        
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
        }
    };
    reader.readAsDataURL(audioBlob);
}

function sendRecordingStatus(isRecording) {
    if (!currentGroup || !socket || socket.readyState !== WebSocket.OPEN) return;
    
    const message = {
        type: "recording_status",
        data: {
            group_id: currentGroup.id,
            is_recording: isRecording
        }
    };
    socket.send(JSON.stringify(message));
}

function createRecordingIndicatorsContainer() {
    const container = document.createElement('div');
    container.id = 'recordingIndicators';
    container.className = 'recording-indicators-container';
    
    // Insert before the message input
    const messageContainer = document.getElementById('messageContainer');
    messageContainer.insertBefore(container, messageContainer.querySelector('.message-input'));
    
    return container;
}
// Handle recording status updates from other users
function handleRecordingStatus(data) {
    if (!currentGroup || data.group_id !== currentGroup.id) return;
    
    const user = allUsers.find(u => u.id === data.user_id);
    if (!user) return;
    
    const recordingContainer = document.getElementById('recordingIndicators') || 
        createRecordingIndicatorsContainer();
    
    if (data.is_recording) {
        // Add or update recording indicator
        let indicator = document.getElementById(`recording-${data.user_id}`);
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = `recording-${data.user_id}`;
            indicator.className = `recording-indicator ${data.user_id === currentUser.id ? 'local-recording' : ''}`;
            
            // Stacked avatar
            const avatar = document.createElement('img');
            avatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`;
            avatar.alt = user.name;
            avatar.className = 'recording-avatar';
            avatar.style.width = '20px';
            avatar.style.height = '20px';
            avatar.style.borderRadius = '50%';
            avatar.style.marginRight = '6px';
            avatar.style.border = '2px solid white';
            
            indicator.innerHTML = `
                <span class="recording-dot"></span>
                <span>${user.name} is recording...</span>
            `;
            
            // Add stop button for local recording
            if (data.user_id === currentUser.id) {
                const stopBtn = document.createElement('button');
                stopBtn.className = 'stop-recording-btn';
                stopBtn.textContent = 'Stop';
                stopBtn.onclick = stopRecording;
                indicator.appendChild(stopBtn);
            }
            
            // Insert avatar at beginning
            indicator.insertBefore(avatar, indicator.firstChild);
            recordingContainer.appendChild(indicator);
        }
    } else {
        // Remove recording indicator
        const indicator = document.getElementById(`recording-${data.user_id}`);
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Hide container if no indicators left
    if (recordingContainer.children.length === 0) {
        recordingContainer.style.display = 'none';
    } else {
        recordingContainer.style.display = 'flex';
    }
}

async function createVoiceMessageElement(messageData) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${messageData.sender_id === currentUser.id ? 'sent' : 'received'}`;
    messageElement.dataset.messageId = messageData.id;
    messageElement.dataset.messageType = "voice";

    const sender = allUsers.find(u => u.id === messageData.sender_id);
    const user = await fetchUser(messageData.sender_id);
    const senderName = user.name;
    
    // Handle reply content if this is a reply
    let replyContent = '';
    let replySender = '';
    if (messageData.reply_to_id) {
        const repliedMessage = await getMessageDetails(messageData.reply_to_id);
        if (repliedMessage) {
            replySender = repliedMessage.sender ? repliedMessage.sender.name : 'Unknown';
            replyContent = repliedMessage.message_type === 'voice' ? 
                '🎙️ Voice Message' : 
                (repliedMessage.content || '[Message]');
        }
    }

    messageElement.innerHTML = `
        <div class="message-header">
            <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(senderName)}&background=random" 
                 alt="${senderName}" class="message-avatar">
            <span class="message-sender">${senderName}</span>
            <span class="message-action" onclick="togglePinMessage(${messageData.id})">
                <i class="fas fa-thumbtack ${messageData.sender_id === currentUser.id ? 'white-icon' : ''} ${messageData.pinned ? 'active' : ''}"></i>
            </span>
        </div>

        ${messageData.reply_to_id ? `
        <div class="message-reply" onclick="navigateToRepliedMessage(event, ${messageData.reply_to_id})">
            <div class="reply-header">
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(replySender)}&background=random"
                     alt="${replySender}" class="tooltip-avatar">
                <div class="message-reply-sender">${replySender}</div>
            </div>
            <div class="message-reply-content">${replyContent}</div>
        </div>` : ''}

        <div class="voice-message">
            <i class="fas fa-microphone"></i>
            <audio controls src="${messageData.audio_data || ''}"></audio>
            <span class="voice-message-duration">${messageData.duration || '0'}s</span>
        </div>

        <div class="message-reactions"></div>

        <div class="message-info ${messageData.sender_id === currentUser.id ? 'sent' : 'received'}">
            <span class="message-time">
                ${new Date(messageData.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                ${messageData.edited_at ? '<span>(edited)</span>' : ''}
            </span>
            ${messageData.pinned ? `<span class="pinned-indicator"><i class="fas fa-thumbtack"></i> Pinned ${formatPinnedDate(new Date(messageData.pinned_at))}</span>` : ''}
        </div>

        <div class="message-actions ${messageData.sender_id === currentUser.id ? 'sent' : 'received'}">
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '👍')">👍</span>
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '❤️')">❤️</span>
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '😂')">😂</span>
            <button class="action-btn reply-btn" title="Reply" onclick="prepareReply(${messageData.id}, '${senderName}')">
                <i class="fas fa-reply"></i>
            </button>
            ${messageData.sender_id === currentUser.id ? `
                <button class="action-btn delete-btn" title="Delete message" onclick="deleteMessage(${messageData.id}, true)">
                    <i class="fas fa-trash"></i>
                </button>
            ` : ''}
        </div>
    `;

    // Add reactions if they exist
    if (messageData.reactions && messageData.reactions.length > 0) {
        const reactionsContainer = messageElement.querySelector('.message-reactions');
        
        const reactionsByEmoji = {};
        messageData.reactions.forEach(reaction => {
            if (!reactionsByEmoji[reaction.emoji]) {
                reactionsByEmoji[reaction.emoji] = [];
            }
            reactionsByEmoji[reaction.emoji].push(reaction);
        });

        for (const [emoji, reactions] of Object.entries(reactionsByEmoji)) {
            const reactionElement = document.createElement('div');
            reactionElement.className = 'reaction-container';

            const emojiElement = document.createElement('span');
            emojiElement.className = 'reaction-emoji';
            emojiElement.textContent = emoji;
            emojiElement.onclick = (e) => {
                e.stopPropagation();
                reactToMessage(messageData.id, emoji);
            };

            const countElement = document.createElement('span');
            countElement.className = 'reaction-count';
            countElement.textContent = reactions.length;

            const tooltip = document.createElement('div');
            tooltip.className = 'reaction-tooltip';
            tooltip.innerHTML = reactions.map(r =>
                `<div class="tooltip-user">
                    <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(r.user.name)}&background=random"
                         alt="${r.user.name}" class="tooltip-avatar">
                    <span>${r.user.name}</span>
                </div>`
            ).join('');

            reactionElement.appendChild(emojiElement);
            reactionElement.appendChild(countElement);
            reactionElement.appendChild(tooltip);

            if (reactions.some(r => r.user_id === currentUser.id)) {
                reactionElement.classList.add('user-reacted');
            }

            reactionsContainer.appendChild(reactionElement);
        }
    }

    return messageElement;
}

async function getMessageDetails(messageId) {
    try {
        const response = await fetch(`/messages/${messageId}`);
        if (!response.ok) throw new Error('Message not found');
        return await response.json();
    } catch (error) {
        console.error('Error fetching message details:', error);
        return null;
    }
}

// Update sendVoiceMessage to include reply_to_id and mentions
function sendVoiceMessage(audioBlob) {
    if (!currentGroup) {
        notificationManager.notify('error', 'Error', 'No group selected');
        return;
    }
    
    // Create a unique filename
    const filename = `voice_${Date.now()}.mp3`;
    
    const reader = new FileReader();
    reader.onload = () => {
        const audioData = reader.result;
        
        const message = {
            type: 'voice_message',
            data: {
                group_id: currentGroup.id,
                audio: audioData,
                duration: Math.round(audioBlob.size / 6000), // Rough estimate
                sender_id: currentUser.id,
                created_at: new Date().toISOString(),
                reply_to_id: messageInput.dataset.replyTo || null,
                mentions: detectMentions(messageInput.value) // Detect mentions from text input if any
            }
        };
        
        cancelReply();
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
        }
    };
    reader.readAsDataURL(audioBlob);
}
// Initialize the application
function init() {
    notificationManager = new NotificationManager();
    loadUsers();
    showHomeScreen();
    // Add these event listeners
    document.getElementById('recordBtn')?.addEventListener('click', startRecording);
    document.getElementById('stopRecordingBtn')?.addEventListener('click', stopRecording);
    messages.addEventListener('scroll', debounce(handleScroll, 200));
    emojiBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        // The actual toggle is handled in emoji-picker.js
    });
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);

    userOptions.forEach(option => {
        option.addEventListener('click', handleUserSelection);
    });

    setupPasswordModalEvents();
    setupMessageInputEvents();

    sendBtn.addEventListener('click', sendMessage);
    createGroupBtn.addEventListener('click', createGroup);
}

async function handleScroll() {
    if (messages.scrollTop < 100 && !isLoadingMessages && !allMessagesLoaded && currentGroup) {
        await loadMessages(currentGroup.id, false);
    }
}

// Utility function to debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

function setupMessageInputEvents() {
    const textarea = document.getElementById('messageInput');
    
    // Auto-resize textarea as user types
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        
        // Also handle typing indicators
        handleTyping();
    });
    
    // Handle Enter key (submit on Enter, new line on Shift+Enter)
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Handle @ mentions
    // textarea.addEventListener('input', handleMentionInput);
    textarea.addEventListener('keydown', function(e) {
        if (e.key === '@') {
            // Show suggestions after a short delay to allow the @ to be inserted
            setTimeout(() => {
                const cursorPos = this.selectionStart;
                const textBeforeCursor = this.value.substring(0, cursorPos);
                const atSymbolIndex = textBeforeCursor.lastIndexOf('@');
                if (atSymbolIndex >= 0) {
                    const searchTerm = textBeforeCursor.substring(atSymbolIndex + 1);
                    showUserSuggestions(searchTerm, atSymbolIndex);
                }
            }, 10);
        }
    });
}

function handleVisibilityChange() {
    if (document.visibilityState === 'visible' && (!socket || socket.readyState !== WebSocket.OPEN)) {
        reconnectWebSocket();
    }
}

function handleOnlineStatus() {
    reconnectWebSocket();
}

function handleOfflineStatus() {
    userStatus.textContent = 'Offline';
    userStatus.className = 'offline';
    notificationManager.notify('system', 'Connection Lost', 'You are currently offline');
}

function handleUserSelection() {
    const userId = this.getAttribute('data-user-id');
    const username = this.getAttribute('data-username');
    showPasswordModal(userId, username);
}

function setupPasswordModalEvents() {
    cancelPasswordBtn.addEventListener('click', () => {
        passwordModal.style.display = 'none';
        passwordInput.value = '';
    });

    submitPasswordBtn.addEventListener('click', verifyPassword);

    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            verifyPassword();
        }
    });
}

function handleMessageInput() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';

    if (this.scrollHeight > 120) {
        this.style.overflowY = 'auto';
    } else {
        this.style.overflowY = 'hidden';
    }
}
async function handleVoiceMessage(messageData) {
    if (currentGroup && messageData.group_id === currentGroup.id) {
        const messageElement = await createVoiceMessageElement(messageData);
        
        // Check if we need to add a date separator
        const messageDate = new Date(messageData.created_at);
        const currentDate = new Date();
        const messageDay = messageDate.toDateString();
        
        let dateLabel = '';
        if (messageDay === currentDate.toDateString()) {
            dateLabel = 'Today';
        } else {
            const yesterday = new Date(currentDate);
            yesterday.setDate(yesterday.getDate() - 1);
            if (messageDay === yesterday.toDateString()) {
                dateLabel = 'Yesterday';
            } else {
                dateLabel = messageDate.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
            }
        }
        
        // Add date separator if needed
        if (!lastMessageDate || lastMessageDate !== dateLabel) {
            const dateSeparator = document.createElement('div');
            dateSeparator.className = 'date-separator';
            dateSeparator.textContent = dateLabel;
            messages.appendChild(dateSeparator);
            lastMessageDate = dateLabel;
        }
        
        messages.appendChild(messageElement);
        scrollToBottom();
    }
}
// WebSocket message handler
// WebSocket message handler
function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);

        // Handle notification type separately
        if (data.type === 'notification') {
            const notification = data.data;
            
            // Determine if this should be a push-only notification
            const isSystemNotification = notification.notification_type === 'system';
            const isPushOnly = isSystemNotification || 
                              notification.notification_type === 'recording_status' ||
                              notification.notification_type === 'typing';
            
            // Add to notification manager with appropriate flags
            notificationManager.notify(
                notification.notification_type,
                notification.title,
                notification.content,
                {
                    ...notification.notification_data,
                    action: {
                        type: 'open_notification',
                        notificationId: notification.id,
                        groupId: notification.notification_data?.group_id,
                        messageId: notification.notification_data?.message_id
                    }
                },
                true, // Always show push notifications
                !isPushOnly // Only add to dropdown if not push-only
            );
            
            // Mark as read if viewed
            if (document.visibilityState === 'visible') {
                fetch('/notifications/mark-read', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({notification_ids: [notification.id]})
                });
            }
            return; // Skip the rest of the handler for notification type
        }

        // Handle other message types
        switch (data.type) {
            case 'new_message':
                handleNewMessage(data.data);
                // For new messages in current group, don't show push notification
                if (!currentGroup || data.data.group_id !== currentGroup.id) {
                    const sender = allUsers.find(u => u.id === data.data.sender_id);
                    const group = findGroupById(data.data.group_id);
                    const groupName = group?.name || `Group ${data.data.group_id}`;
                    const title = `New message in ${groupName}`;
                    const message = sender ? 
                        `${sender.name}: ${data.data.content.substring(0, 50)}${data.data.content.length > 50 ? '...' : ''}` : 
                        `New message: ${data.data.content.substring(0, 50)}${data.data.content.length > 50 ? '...' : ''}`;

                    notificationManager.notify(
                        'message',
                        title,
                        message,
                        {
                            group_id: data.data.group_id,
                            message_id: data.data.id,
                            action: {
                                type: 'open_message',
                                messageId: data.data.id,
                                groupId: data.data.group_id
                            }
                        },
                        true, // Show push notification
                        true  // Add to dropdown
                    );
                }
                break;

            case 'voice_message':
                handleVoiceMessage(data.data);
                // Similar handling as new_message but for voice
                if (!currentGroup || data.data.group_id !== currentGroup.id) {
                    const sender = allUsers.find(u => u.id === data.data.sender_id);
                    const group = findGroupById(data.data.group_id);
                    const groupName = group?.name || `Group ${data.data.group_id}`;
                    const title = `New voice message in ${groupName}`;
                    const message = sender ? 
                        `${sender.name} sent a voice message` : 
                        `New voice message received`;

                    notificationManager.notify(
                        'voice_message',
                        title,
                        message,
                        {
                            group_id: data.data.group_id,
                            message_id: data.data.id,
                            action: {
                                type: 'open_message',
                                messageId: data.data.id,
                                groupId: data.data.group_id
                            }
                        },
                        true, // Show push notification
                        true  // Add to dropdown
                    );
                }
                break;

            case 'message_updated':
                handleMessageUpdated(data.data);
                break;

            case 'message_deleted':
                handleMessageDeleted(data.data);
                break;

            case 'pin_message':
                handleMessagePinned(data.data);
                // Only show push notification if someone else pinned the message
                if (data.data.user_id !== currentUser.id) {
                    const sender = allUsers.find(u => u.id === data.data.user_id);
                    const message = getMessageDetails(data.data.message_id);
                    const title = 'Message Pinned';
                    const content = sender ? 
                        `${sender.name} pinned a message` : 
                        `A message was pinned`;

                    notificationManager.notify(
                        'system',
                        title,
                        content,
                        {
                            group_id: data.data.group_id,
                            message_id: data.data.message_id,
                            action: {
                                type: 'open_message',
                                messageId: data.data.message_id,
                                groupId: data.data.group_id
                            }
                        },
                        true,  // Show push notification
                        false  // Don't add to dropdown (system notification)
                    );
                }
                break;

            case 'reaction_change':
                handleReactionChange(data.data);
                break;

            case 'mention':
                handleMentionNotification(data.data);
                // Mention notifications are always important
                const mentioner = allUsers.find(u => u.id === data.data.mentioned_by);
                const groupName = currentGroup ? currentGroup.name : `Group ${data.data.group_id}`;
                
                notificationManager.notify(
                    'mention', 
                    `You were mentioned in ${groupName}`,
                    mentioner ? `${mentioner.name} mentioned you: ${data.data.content}` : `You were mentioned in a message`,
                    {
                        action: { 
                            type: 'open_message', 
                            messageId: data.data.message_id,
                            groupId: data.data.group_id
                        }
                    },
                    true,  // Show push notification
                    true   // Add to dropdown
                );
                break;

            case 'user_joined':
            case 'user_left':
                handleUserPresenceChange(data.type, data.data);
                // User presence changes are system notifications
                if (currentGroup && data.data.group_id === currentGroup.id) {
                    const user = allUsers.find(u => u.id === data.data.user_id);
                    const username = user ? user.name : `User ${data.data.user_id}`;
                    const action = data.type === 'user_joined' ? 'joined' : 'left';
                    
                    notificationManager.notify(
                        'system',
                        'User Activity',
                        `${username} ${action} the group`,
                        {
                            groupId: data.data.group_id,
                            userId: data.data.user_id
                        },
                        true,  // Show push notification
                        false  // Don't add to dropdown
                    );
                }
                break;

            case 'new_group':
            case 'group_created':
                handleGroupEvent(data.type, data.data);
                // Only show notification if it's not our own group creation
                if (currentUser && data.data.created_by !== currentUser.id) {
                    notificationManager.notify(
                        'system',
                        'New Group',
                        `New group created: ${data.data.name}`,
                        {
                            groupId: data.data.id,
                            action: { type: 'open_group', groupId: data.data.id }
                        },
                        true,  // Show push notification
                        true   // Add to dropdown
                    );
                }
                break;

            case 'error':
                handleErrorEvent(data.data);
                notificationManager.notify(
                    'error',
                    'Error',
                    data.data.message || 'An error occurred',
                    {},
                    true,  // Show push notification
                    true   // Add to dropdown (errors are important)
                );
                break;

            case 'online_users':
                handleOnlineUsersUpdate(data.data);
                if (currentGroup && data.data.group_id === currentGroup.id) {
                    if (!data.data.users.includes(currentUser.id)) {
                        data.data.users.push(currentUser.id);
                    }
                    updateOnlineUsers(data.data.users);
                }
                break;

            case 'reaction_added':
                handleReactionAdded(data.data);
                break;

            case 'reaction_removed':
                handleReactionRemoved(data.data);
                break;

            case 'reactions_updated':
                handleReactionsUpdated(data.data);
                break;
            
            case 'notification':
    const notification = data.data;
    
    // Determine if this should be stored in the database
    const shouldStore = !(notification.notification_type === 'typing' || 
                         notification.notification_type === 'recording_status');
    
    if (shouldStore) {
        // Send notification to backend to be stored
        try {
            const response = fetch('/notifications/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: currentUser.id,
                    notification_type: notification.notification_type,
                    title: notification.title,
                    content: notification.content,
                    message_id: notification.notification_data?.message_id,
                    group_id: notification.notification_data?.group_id,
                    notification_data: notification.notification_data
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to store notification');
            }
            
            // Get the stored notification with ID from server
            const storedNotification = response.json();
            notification.id = storedNotification.id;
            
        } catch (error) {
            console.error('Error storing notification:', error);
            // Fall back to client-side ID if storage fails
            notification.id = Date.now();
        }
    } else {
        // For transient notifications, use a timestamp ID
        notification.id = Date.now();
    }
    
    // Add to notification manager
    notificationManager.notify(
        notification.notification_type,
        notification.title,
        notification.content,
        {
            ...notification.notification_data,
            action: {
                type: 'open_notification',
                notificationId: notification.id,
                groupId: notification.notification_data?.group_id,
                messageId: notification.notification_data?.message_id
            }
        },
        true, // Show push notification
        shouldStore // Only add to dropdown if stored
    );
    
    // Refresh the notification list if stored
    if (shouldStore) {
        loadNotifications();
    }
    break;
                
            case 'typing':
                handleTypingNotification(data.data);
                // Typing indicators are push-only
                if (data.data.user_id !== currentUser.id) {
                    const user = allUsers.find(u => u.id === data.data.user_id);
                    if (user && data.data.is_typing) {
                        notificationManager.notify(
                            'typing',
                            `${user.name} is typing`,
                            `In ${currentGroup?.name || 'the group'}`,
                            {
                                group_id: data.data.group_id,
                                user_id: data.data.user_id
                            },
                            true,  // Show push notification
                            false  // Don't add to dropdown
                        );
                    }
                }
                break;

            case 'recording_status':
                handleRecordingStatus(data.data);
                // Recording status is push-only
                if (data.data.user_id !== currentUser.id && data.data.is_recording) {
                    const user = allUsers.find(u => u.id === data.data.user_id);
                    if (user) {
                        notificationManager.notify(
                            'recording_status',
                            `${user.name} started recording`,
                            `In ${currentGroup?.name || 'the group'}`,
                            {
                                group_id: data.data.group_id,
                                user_id: data.data.user_id
                            },
                            true,  // Show push notification
                            false  // Don't add to dropdown
                        );
                    }
                }
                break;

            default:
                console.log('Unknown message type:', data.type);
        }
    } catch (error) {
        console.error('Error processing WebSocket message:', error);
        notificationManager.notify(
            'error',
            'Message Error',
            'Failed to process incoming message',
            {},
            true,  // Show push notification
            true   // Add to dropdown
        );
    }
}

// Helper function to find group by ID
function findGroupById(groupId) {
    const groupItem = document.querySelector(`.group-item[data-group-id="${groupId}"]`);
    if (groupItem) {
        return {
            id: groupId,
            name: groupItem.querySelector('h4').textContent
        };
    }
    return null;
}


async function loadNotifications() {
    if (!currentUser) return;
    
    try {
        // Load both read and unread notifications
        const response = await fetch(`/users/${currentUser.id}/notifications?limit=50`);
        const notifications = await response.json();
        
        // Clear existing notifications
        notificationManager.clearAllNotifications();
        
        // Add new notifications
        notifications.forEach(notif => {
            notificationManager.addToQueue({
                id: notif.id,
                type: notif.notification_type,
                title: notif.title,
                message: notif.content,
                data: notif.notification_data || {},
                timestamp: new Date(notif.created_at),
                read: notif.is_read
            });
        });
        
        // Update the UI
        notificationManager.updateUI();
        
        // Load unread count separately
        await updateUnreadCount();
        
    } catch (error) {
        console.error('Error loading notifications:', error);
        notificationManager.notify('error', 'Load Error', 'Failed to load notifications');
    }
}

async function updateUnreadCount() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`/users/${currentUser.id}/notifications/unread-count`);
        const count = await response.json();
        
        // Update the badge with the unread count
        notificationManager.updateBadge(count);
        
    } catch (error) {
        console.error('Error loading unread count:', error);
    }
}
async function fetchGroup(groupId) {
    try {
        const response = await fetch(`/groups/${groupId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Group not found');
            }
            throw new Error('Failed to fetch group');
        }
        
        const groupData = await response.json();
        return groupData;
        
    } catch (error) {
        console.error('Error fetching group:', error);
        notificationManager.notify('error', 'Group Error', error.message);
        return null;
    }
}
async function fetchUser(userId) {
    try {
        const response = await fetch(`/users/${userId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Group not found');
            }
            throw new Error('Failed to fetch group');
        }
        
        const groupData = await response.json();
        return groupData;
        
    } catch (error) {
        console.error('Error fetching group:', error);
        notificationManager.notify('error', 'Group Error', error.message);
        return null;
    }
}
async function handleNewMessage(messageData) {
    if (currentGroup && messageData.group_id === currentGroup.id) {
        await addMessageToChat(messageData, 'append');
        scrollToBottom();
    } else {
        const sender = allUsers.find(u => u.id === messageData.sender_id);
        const group = await fetchGroup(messageData.group_id);
        const groupName = group.name;
        const title = `New message in ${groupName}`;
        const message = sender ? `${sender.name}: ${messageData.content.substring(0, 50)}...`
            : `New message: ${messageData.content.substring(0, 50)}...`;

        notificationManager.notify('message', title, message, {
            senderId: messageData.sender_id,
            groupId: messageData.group_id,
            action: { type: 'open_group', groupId: messageData.group_id }
        });
    }
}

function handleMentionNotification(data) {
    // Highlight the group in sidebar if not current group
    if (!currentGroup || data.group_id !== currentGroup.id) {
        const groupItem = document.querySelector(`.group-item[data-group-id="${data.group_id}"]`);
        if (groupItem) {
            // Add visual indicator
            groupItem.classList.add('mentioned');
            
            // Update unread count
            updateGroupUnreadCount(data.group_id);
        }
    }
    
    // Show notification
    const mentioner = allUsers.find(u => u.id === data.mentioned_by);
    const groupName = currentGroup ? currentGroup.name : `Group ${data.group_id}`;
    
    notificationManager.notify('direct', 
        `You were mentioned in ${groupName}`,
        mentioner ? `${mentioner.name} mentioned you: ${data.content}`
                  : `You were mentioned in a message`,
        {
            action: { 
                type: 'open_message', 
                messageId: data.message_id,
                groupId: data.group_id
            }
        }
    );
    
    // Play special sound for mentions
    notificationManager.playSound('mention');
}

function updateGroupUnreadCount(groupId) {
    const groupItem = document.querySelector(`.group-item[data-group-id="${groupId}"]`);
    if (groupItem) {
        const unreadBadge = groupItem.querySelector('.group-item-unread');
        if (unreadBadge) {
            const currentCount = parseInt(unreadBadge.textContent) || 0;
            unreadBadge.textContent = currentCount + 1;
            unreadBadge.style.display = 'flex';
        } else {
            const newBadge = document.createElement('div');
            newBadge.className = 'group-item-unread';
            newBadge.textContent = '1';
            newBadge.style.display = 'flex';
            groupItem.appendChild(newBadge);
        }
    }
}

function handleUserPresenceChange(type, data) {
    if (currentGroup && data.group_id === currentGroup.id) {
        updateOnlineUsers(data.online_users);

        const user = allUsers.find(u => u.id === data.user_id);
        const username = user ? user.name : `User ${data.user_id}`;
        const action = type === 'user_joined' ? 'joined' : 'left';

        notificationManager.notify('system', 'User Activity', `${username} ${action} the group`, {
            groupId: data.group_id,
            userId: data.user_id
        });
    }
}

function handleGroupEvent(type, data) {
    if (type === 'new_group') {
        // Check if this group already exists in the sidebar
        const existing = document.querySelector(`.group-item[data-group-id="${data.id}"]`);
        if (!existing) {
            addGroupToSidebar(data);

            // Only show notification if it's not our own group creation
            if (currentUser && data.created_by !== currentUser.id) {
                notificationManager.notify('system', 'New Group', `New group created: ${data.name}`, {
                    groupId: data.id,
                    action: { type: 'open_group', groupId: data.id }
                });
            }
        }
    }
}

function handleErrorEvent(data) {
    notificationManager.notify('error', 'Error', data.message || 'An error occurred');
}

function login(data) {
    isManualDisconnect = false;
    currentUser = {
        id: data.id,
        username: data.username,
        name: data.name,
        avatar: data.avatar,
        is_online: data.is_online
    };
    document.querySelector('.notification-container').style.display = 'block';
    usernameDisplay.textContent = data.name;
    userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.name)}&background=random`;
    userStatus.textContent = 'Online';
    userStatus.className = 'online';

    loginPanel.style.display = 'none';
    chatInterface.style.display = 'flex';

    connectWebSocket();
    loadGroups();

    notificationManager.notify('success', 'Login Successful', `Welcome back, ${data.name}!`);
}

function connectWebSocket() {
    if (isManualDisconnect) return;

    if (socket) {
        socket.onopen = null;
        socket.onclose = null;
        socket.onerror = null;
        if (socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    }

    if (reconnectTimeoutId) {
        clearTimeout(reconnectTimeoutId);
        reconnectTimeoutId = null;
    }

    userStatus.textContent = 'Connecting...';
    userStatus.className = 'connecting';

    try {
        socket = new WebSocket(`ws://${window.location.host}/wss/${currentUser.id}`);

        socket.onopen = () => {
            console.log('WebSocket connected');
            reconnectAttempts = 0;
            userStatus.textContent = 'Online';
            userStatus.className = 'online';
            notificationManager.notify('success', 'Connection Established', 'Connected to chat server');

            if (currentGroup) {
                joinGroup(currentGroup.id);
            }
        };

        socket.onclose = (event) => {
            console.log('WebSocket disconnected', event);
            userStatus.textContent = 'Offline';
            userStatus.className = 'offline';

            if (!isManualDisconnect) {
                notificationManager.notify('error', 'Connection Lost', 'Attempting to reconnect...');
                scheduleReconnect();
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            notificationManager.notify('error', 'Connection Error', 'A WebSocket error occurred');
            socket.close();
        };

        socket.onmessage = handleWebSocketMessage;

    } catch (error) {
        console.error('WebSocket initialization error:', error);
        notificationManager.notify('error', 'Connection Error', 'Failed to initialize WebSocket');
        scheduleReconnect();
    }
}

function scheduleReconnect() {
    if (isManualDisconnect || reconnectAttempts >= maxReconnectAttempts) {
        console.log('Max reconnection attempts reached or manual disconnect');
        return;
    }

    reconnectAttempts++;
    const delay = calculateReconnectDelay(reconnectAttempts);

    console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts}) in ${delay}ms`);

    reconnectTimeoutId = setTimeout(() => {
        connectWebSocket();
    }, delay);
}

function calculateReconnectDelay(attempt) {
    const jitter = Math.random() * 500;
    return Math.min(baseReconnectDelay * Math.pow(2, attempt - 1) + jitter, 30000);
}

function disconnectWebSocket() {
    isManualDisconnect = true;
    if (socket) {
        socket.close();
    }
    if (reconnectTimeoutId) {
        clearTimeout(reconnectTimeoutId);
        reconnectTimeoutId = null;
    }
}

function reconnectWebSocket() {
    isManualDisconnect = false;
    reconnectAttempts = 0;
    connectWebSocket();
}

function loadUsers() {
    fetch('/users/')
        .then(response => response.json())
        .then(users => {
            allUsers = users;
            renderUserList(users);
        })
        .catch(error => {
            console.error('Error loading users:', error);
            notificationManager.notify('error', 'Load Error', 'Failed to load users');
        });
}

function renderUserList(users) {
    const userList = document.getElementById('userList');
    userList.innerHTML = '';

    users.forEach(user => {
        const userOption = document.createElement('div');
        userOption.className = 'user-option';
        userOption.dataset.userId = user.id;
        userOption.dataset.username = user.name;

        const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`;

        userOption.innerHTML = `
            <img src="${avatarUrl}" alt="${user.name}">
            <div class="user-info">
                <span class="username">${user.name}</span>
                <span class="status ${user.is_online ? 'online' : 'offline'}">
                    ${user.is_online ? 'Online' : 'Offline'}
                </span>
            </div>
        `;

        userOption.addEventListener('click', () => {
            showPasswordModal(user);
        });

        userList.appendChild(userOption);
    });
}

function showPasswordModal(user) {
    selectedUsernameDisplay.textContent = user.name;
    passwordModal.style.display = 'flex';
    passwordInput.focus();
    passwordModal.dataset.userId = user.id;
    passwordModal.dataset.username = user.username;
}

function verifyPassword() {
    const userId = passwordModal.dataset.userId;
    const username = passwordModal.dataset.username;

    if (!username) {
        notificationManager.notify('error', 'Validation Error', 'Please enter your username');
        return;
    }

    authenticateUser(username);
}

function authenticateUser(username) {
    fetch('/auth/login/' + username, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Authentication failed');
            }
            return response.json();
        })
        .then(data => {
            passwordModal.style.display = 'none';
            passwordInput.value = '';
            login(data);
        })
        .catch(error => {
            console.error('Authentication error:', error);
            notificationManager.notify('error', 'Login Failed', 'Invalid credential. Please try again.');
            passwordInput.value = '';
            passwordInput.focus();
        });
}

function loadGroups() {
    fetch('/groups/')
        .then(response => response.json())
        .then(groups => {
            groupList.innerHTML = '';
            groups.forEach(group => {
                addGroupToSidebar(group);
            });
            notificationManager.notify('success', 'Groups Loaded', `Loaded ${groups.length} groups`);
        })
        .catch(error => {
            console.error('Error loading groups:', error);
            notificationManager.notify('error', 'Load Error', 'Failed to load groups');
        });
}

// Helper function to sort groups alphabetically
function sortGroupList() {
    const container = groupList;
    const items = Array.from(container.querySelectorAll('.group-item'));

    items.sort((a, b) => {
        const nameA = a.querySelector('h4').textContent.toLowerCase();
        const nameB = b.querySelector('h4').textContent.toLowerCase();
        return nameA.localeCompare(nameB);
    });

    items.forEach(item => container.appendChild(item));
}
function getUserName(userId) {
    const user = allUsers.find(u => u.id === userId);
    return user ? user.name : `User ${userId}`;
}

// Helper function to add group to sidebar
function addGroupToSidebar(group) {
    // Check if group already exists
    const existing = document.querySelector(`.group-item[data-group-id="${group.id}"]`);
    if (existing) return;

    const groupItem = document.createElement('div');
    groupItem.className = 'group-item';
    groupItem.dataset.groupId = group.id;

    // Use the group's name and description
    const groupName = group.name || `Group ${group.id}`;
    const groupDescription = group.description || 'No description';
    const createdBy = group.created_by || group.creator_id; // Handle different backend field names

    groupItem.innerHTML = `
        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(groupName)}&background=random" alt="${groupName}">
        <div class="group-item-info">
            <h4>${groupName}</h4>
            <p>${groupDescription}</p>
            ${createdBy ? `<small>Created by ${getUserName(createdBy)}</small>` : ''}
        </div>
        <div class="group-item-unread" style="display: none;">0</div>
    `;

    groupItem.addEventListener('click', () => {
        selectGroup(group);
        // Reset unread count when selected
        groupItem.querySelector('.group-item-unread').style.display = 'none';
    });

    groupList.appendChild(groupItem);

    // Sort groups alphabetically
    // sortGroupList();
}

async function fetchPinnedMessages(groupId) {
    try {
        const response = await fetch(`/groups/${groupId}/pinned-messages`);
        if (!response.ok) throw new Error('Failed to fetch pinned messages');
        return await response.json();
    } catch (error) {
        console.error('Error fetching pinned messages:', error);
        return [];
    }
}

async function selectGroup(group) {
    try {
        // Reset loading states
        isLoadingMessages = false;
        allMessagesLoaded = false;
        messagePage = 1;
        clearPinnedMessages();
        // Clear unread count
        const groupItem = document.querySelector(`.group-item[data-group-id="${group.id}"]`);
        if (groupItem) {
            const unreadBadge = groupItem.querySelector('.group-item-unread');
            if (unreadBadge) {
                unreadBadge.style.display = 'none';
            }
        }

        // Show loading state
        currentGroupName.textContent = 'Joining...';
        messages.innerHTML = '<div class="loading-message">Loading group...</div>';

        // Clear any existing typing indicators
        typingUsers = {};
        updateTypingIndicator();

        // Join the group first
        const joined = await joinGroup(group.id);
        if (!joined) {
            throw new Error('Failed to join group');
        }

        // Now proceed with selection
        currentGroup = group;

        document.querySelectorAll('.group-item').forEach(item => {
            item.classList.remove('active');
        });

        document.querySelector(`.group-item[data-group-id="${group.id}"]`).classList.add('active');
        currentGroupName.textContent = group.name;

        homeScreen.style.display = 'none';
        main_chat.style.display = 'flex';
        rightPanel.style.display = 'flex';

        // Clear existing messages and load new ones
        messages.innerHTML = '';
        await loadMessages(group.id);
        getOnlineUsers(group.id);

    } catch (error) {
        console.error('Error selecting group:', error);
        notificationManager.notify('error', 'Group Error', error.message);
        showHomeScreen();
    }
}

function showHomeScreen() {
    currentGroup = null;
    homeScreen.style.display = 'block';
    main_chat.style.display = 'none';
    currentGroupName.textContent = 'Select a group';
    document.getElementById('rightPanel').classList.remove('visible');

    document.querySelectorAll('.group-item').forEach(item => {
        item.classList.remove('active');
    });

    // Clear messages
    messages.innerHTML = '';
    clearPinnedMessages();
    groupMembers.innerHTML = '';
    messageInput.value = '';
    messageInput.style.height = 'auto';
}

async function joinGroup(groupId) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        notificationManager.notify('error', 'Connection Error', 'Not connected to server');
        return false;
    }

    try {
        const groupItem = document.querySelector(`.group-item[data-group-id="${groupId}"]`);
        if (groupItem) {
            groupItem.classList.add('joining');
        }
        // Immediately add yourself to the online users list
        if (currentUser) {
            updateOnlineUsers([currentUser.id]);
        }

        // Create a promise to handle the join response
        return new Promise((resolve, reject) => {
            const handler = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'online_users' && data.data.group_id === groupId) {
                        socket.removeEventListener('message', handler);
                        resolve(true);
                    } else if (data.type === 'error' && data.data.group_id === groupId) {
                        socket.removeEventListener('message', handler);
                        reject(new Error(data.data.message));
                    }
                } catch (error) {
                    socket.removeEventListener('message', handler);
                    reject(error);
                }
            };

            socket.addEventListener('message', handler);

            // Set timeout
            setTimeout(() => {
                socket.removeEventListener('message', handler);
                reject(new Error('Join timeout'));
            }, 5000);

            // Send join message
            const joinMsg = {
                type: 'join_group',
                data: { group_id: groupId }
            };
            socket.send(JSON.stringify(joinMsg));
        });
    } catch (error) {
        console.error('Join group error:', error);
        notificationManager.notify('error', 'Group Error', error.message);
        return false;
    } finally {
        const groupItem = document.querySelector(`.group-item[data-group-id="${groupId}"]`);
        if (groupItem) {
            groupItem.classList.remove('joining');
        }
    }
}

async function createVoiceMessageElement(messageData) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${messageData.sender_id === currentUser.id ? 'sent' : 'received'}`;
    messageElement.dataset.messageId = messageData.id;
    messageElement.dataset.messageType = "voice";

    const sender = allUsers.find(u => u.id === messageData.sender_id);
    const user = await fetchUser(messageData.sender_id);
    const senderName = user.name;
    
    // Handle reply content if this is a reply
    let replyContent = '';
    let replySender = '';
    if (messageData.reply_to_id) {
        const repliedMessage = await getMessageDetails(messageData.reply_to_id);
        if (repliedMessage) {
            replySender = repliedMessage.sender ? repliedMessage.sender.name : 'Unknown';
            replyContent = repliedMessage.message_type === 'voice' ? 
                '🎙️ Voice Message' : 
                (repliedMessage.content || '[Message]');
        }
    }

    messageElement.innerHTML = `
        <div class="message-header">
            <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(senderName)}&background=random" 
                 alt="${senderName}" class="message-avatar">
            <span class="message-sender">${senderName}</span>
            <!-- Removed the pin icon from here -->
        </div>

        ${messageData.reply_to_id ? `
        <div class="message-reply" onclick="navigateToRepliedMessage(event, ${messageData.reply_to_id})">
            <div class="reply-header">
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(replySender)}&background=random"
                     alt="${replySender}" class="tooltip-avatar">
                <div class="message-reply-sender">${replySender}</div>
            </div>
            <div class="message-reply-content">${replyContent}</div>
        </div>` : ''}

        <div class="voice-message">
            <i class="fas fa-microphone"></i>
            <audio controls src="${messageData.audio_data || ''}"></audio>
            <span class="voice-message-duration">${messageData.duration || '0'}s</span>
        </div>

        <div class="message-reactions"></div>

        <div class="message-info ${messageData.sender_id === currentUser.id ? 'sent' : 'received'}">
            <span class="message-time">
                ${new Date(messageData.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                ${messageData.edited_at ? '<span>(edited)</span>' : ''}
            </span>
            ${messageData.pinned ? `<span class="pinned-indicator"><i class="fas fa-thumbtack"></i> Pinned ${formatPinnedDate(new Date(messageData.pinned_at))}</span>` : ''}
        </div>

        <div class="message-actions ${messageData.sender_id === currentUser.id ? 'sent' : 'received'}">
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '👍')">👍</span>
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '❤️')">❤️</span>
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '😂')">😂</span>
            <button class="action-btn reply-btn" title="Reply" onclick="prepareReply(${messageData.id}, '${senderName}')">
                <i class="fas fa-reply"></i>
            </button>
            ${messageData.sender_id === currentUser.id ? `
                <button class="action-btn delete-btn" title="Delete message" onclick="deleteMessage(${messageData.id}, true)">
                    <i class="fas fa-trash"></i>
                </button>
            ` : ''}
        </div>
    `;

    // Add reactions if they exist
    if (messageData.reactions && messageData.reactions.length > 0) {
        const reactionsContainer = messageElement.querySelector('.message-reactions');
        
        const reactionsByEmoji = {};
        messageData.reactions.forEach(reaction => {
            if (!reactionsByEmoji[reaction.emoji]) {
                reactionsByEmoji[reaction.emoji] = [];
            }
            reactionsByEmoji[reaction.emoji].push(reaction);
        });

        for (const [emoji, reactions] of Object.entries(reactionsByEmoji)) {
            const reactionElement = document.createElement('div');
            reactionElement.className = 'reaction-container';

            const emojiElement = document.createElement('span');
            emojiElement.className = 'reaction-emoji';
            emojiElement.textContent = emoji;
            emojiElement.onclick = (e) => {
                e.stopPropagation();
                reactToMessage(messageData.id, emoji);
            };

            const countElement = document.createElement('span');
            countElement.className = 'reaction-count';
            countElement.textContent = reactions.length;

            const tooltip = document.createElement('div');
            tooltip.className = 'reaction-tooltip';
            tooltip.innerHTML = reactions.map(r =>
                `<div class="tooltip-user">
                    <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(r.user.name)}&background=random"
                         alt="${r.user.name}" class="tooltip-avatar">
                    <span>${r.user.name}</span>
                </div>`
            ).join('');

            reactionElement.appendChild(emojiElement);
            reactionElement.appendChild(countElement);
            reactionElement.appendChild(tooltip);

            if (reactions.some(r => r.user_id === currentUser.id)) {
                reactionElement.classList.add('user-reacted');
            }

            reactionsContainer.appendChild(reactionElement);
        }
    }

    return messageElement;
}

async function getMessageDetails(messageId) {
    try {
        const response = await fetch(`/messages/${messageId}`);
        if (!response.ok) throw new Error('Message not found');
        return await response.json();
    } catch (error) {
        console.error('Error fetching message details:', error);
        return null;
    }
}

// Update sendVoiceMessage to include reply_to_id and mentions
function sendVoiceMessage(audioBlob) {
    if (!currentGroup) {
        notificationManager.notify('error', 'Error', 'No group selected');
        return;
    }
    
    // Create a unique filename
    const filename = `voice_${Date.now()}.mp3`;
    
    const reader = new FileReader();
    reader.onload = () => {
        const audioData = reader.result;
        
        const message = {
            type: 'voice_message',
            data: {
                group_id: currentGroup.id,
                audio: audioData,
                duration: Math.round(audioBlob.size / 6000), // Rough estimate
                sender_id: currentUser.id,
                created_at: new Date().toISOString(),
                reply_to_id: messageInput.dataset.replyTo || null,
                mentions: detectMentions(messageInput.value) // Detect mentions from text input if any
            }
        };
        
        cancelReply();
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
        }
    };
    reader.readAsDataURL(audioBlob);
}

// Update loadMessages to show pinned status
async function loadMessages(groupId, initialLoad = true) {
    if (isLoadingMessages || allMessagesLoaded) return;
    
    isLoadingMessages = true;
    
    try {
        // Show loading indicator if this is the initial load
        if (initialLoad) {
            messages.innerHTML = '<div class="loading-message">Loading messages...</div>';
            messagePage = 1;
            allMessagesLoaded = false;
        }else {
            // Add loading indicator for older messages
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'loading-older';
            messages.insertBefore(loadingIndicator, messages.firstChild);
        }
        
        const response = await fetch(`/groups/${groupId}/messages?page=${messagePage}&limit=${MESSAGES_PER_PAGE}`);
        const messagesData = await response.json();
        
        if (!initialLoad) {
            const loadingIndicator = messages.querySelector('.loading-older');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
        }

        if (messagesData.length === 0) {
            allMessagesLoaded = true;
            if (initialLoad) {
                messages.innerHTML = '<div class="no-messages">Let get Started</div>';
            } else {
                // Add "no more messages" indicator
                const noMoreMessages = document.createElement('div');
                noMoreMessages.className = 'no-messages';
                noMoreMessages.textContent = 'No older messages';
                messages.insertBefore(noMoreMessages, messages.firstChild);
            }
            return;
        }
        
        // Reverse the array for initial load (newest first)
        const messagesToDisplay = initialLoad ? messagesData.reverse() : messagesData;
        
        // Clear messages only on initial load
        if (initialLoad) {
            messages.innerHTML = '';
        }
        
        // Track scroll position before adding new messages
        const wasAtBottom = isScrolledToBottom();
        const oldScrollHeight = messages.scrollHeight;
        const oldScrollTop = messages.scrollTop;
        
        // Process messages
        for (const message of messagesToDisplay) {
            await addMessageToChat(message, initialLoad ? 'append' : 'prepend');
        }
        
        // Handle pinned messages
        const pinnedMessages = messagesData.filter(m => m.pinned);
        for (const message of pinnedMessages) {
            const messageElement = document.querySelector(`.message[data-message-id="${message.id}"]`);
            if (messageElement) {
                messageElement.classList.add('pinned');
                addToPinnedMessages({
                    ...message,
                    pinned_at: message.pinned_at || message.created_at
                });
            }
        }
        
        // Scroll handling
        if (initialLoad) {
            scrollToBottom();
        } else {
            // Maintain scroll position when loading older messages
            const newSscrollHeight = messages.scrollHeight;
            messages.scrollTop = oldScrollTop + (newSscrollHeight - oldScrollHeight);
        }
        
        // Increment page counter for next load
        messagePage++;
        
    } catch (error) {
        console.error('Error loading messages:', error);
        notificationManager.notify('error', 'Load Error', 'Failed to load messages');
    } finally {
        isLoadingMessages = false;
    }
}

function isScrolledToBottom() {
    const { scrollTop, scrollHeight, clientHeight } = messages;
    return scrollTop + clientHeight >= scrollHeight - 50; // 50px buffer
}

function clearPinnedMessages() {
    const pinnedList = document.querySelector('.pinned-list');
    if (pinnedList) {
        pinnedList.innerHTML = '';
    }
}

function detectMentions(content) {
    const mentionRegex = /@(\w+)/g;
    const matches = [...content.matchAll(mentionRegex)];
    return matches.map(match => {
        const username = match[1];
        const user = allUsers.find(u => u.username === username);
        return user ? user.id : null;
    }).filter(id => id !== null);
}

function sendMessage() {
    const content = messageInput.value.trim();
    const replyToId = messageInput.dataset.replyTo || null;
    
    if (!content) {
        notificationManager.notify('error', 'Validation Error', 'Message cannot be empty');
        return;
    }
    
    if (!currentGroup) {
        notificationManager.notify('error', 'Validation Error', 'No group selected');
        return;
    }
    
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        notificationManager.notify('error', 'Connection Error', 'Not connected to server');
        return;
    }

    // Detect mentions in the message
    const mentions = detectMentions(content);

    const message = {
        type: 'new_message',
        data: {
            group_id: currentGroup.id,
            content: content,
            sender_id: currentUser.id,
            reply_to_id: replyToId,
            mentions: mentions
        }
    };
    
    // Send the message
    socket.send(JSON.stringify(message));
    
    // Immediately send a "stopped typing" notification
    if (socket && socket.readyState === WebSocket.OPEN) {
        const typingMessage = {
            type: 'typing',
            data: {
                group_id: currentGroup.id,
                is_typing: false
            }
        };
        socket.send(JSON.stringify(typingMessage));
    }
    
    // Clear the input and reset UI
    messageInput.value = '';
    messageInput.style.height = 'auto';
    cancelReply();
    
    // Clear any local typing indicators
    delete typingUsers[currentUser.id];
    updateTypingIndicator();
}


function togglePinMessage(messageId) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        notificationManager.notify('error', 'Connection Error', 'Not connected to server');
        return;
    }

    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    const isCurrentlyPinned = messageElement.classList.contains('pinned');
    const pinIcon = messageElement.querySelector('.message-action .fa-thumbtack');
    const pinnedIndicator = messageElement.querySelector('.pinned-indicator');
    
    const message = {
        type: 'pin_message',
        data: {
            message_id: messageId,
            pin: !isCurrentlyPinned,
            user_id: currentUser.id  // Send current user ID
        }
    };

    socket.send(JSON.stringify(message));

     // Optimistically update UI
        if (isCurrentlyPinned) {
            // Unpinning
            messageElement.classList.remove('pinned');
            pinIcon.classList.remove('active');
            if (pinnedIndicator) {
                pinnedIndicator.remove();
            }
            removeFromPinnedMessages(messageId);
        } else {
            // Pinning
            messageElement.classList.add('pinned');
            pinIcon.classList.add('active');
            
            // Create or update pinned indicator
            if (!pinnedIndicator) {
                const messageInfo = messageElement.querySelector('.message-info');
                if (messageInfo) {
                    const newPinnedIndicator = document.createElement('span');
                    newPinnedIndicator.className = 'pinned-indicator';
                    newPinnedIndicator.innerHTML = `<i class="fas fa-thumbtack"></i> Pinned ${formatPinnedDate(new Date())}`;
                    messageInfo.appendChild(newPinnedIndicator);
                }
            }
            
         }
    if (!messageElement) return;     
}
// Add these helper functions
function addToPinnedMessages(messageData) {
    
    // Remove existing pinned message if it exists (for updates)
    const existingPinned = document.querySelector(`.pinned-message[data-message-id="${messageData.id}"]`);
    if (existingPinned) {
        existingPinned.remove();
    }

    const messageElement = document.querySelector(`.message[data-message-id="${messageData.id}"]`);
    if (!messageElement) return;

    const pinnedList = document.querySelector('.pinned-list');
    const pinnedItem = document.createElement('div');
    pinnedItem.className = 'pinned-message';
    pinnedItem.dataset.messageId = messageData.id;
    pinnedItem.dataset.groupId = messageData.group_id;

    // Use pinned_at if available, otherwise fall back to current time
    const timestamp = messageData.pinned_at ? new Date(messageData.pinned_at) : new Date();
    pinnedItem.dataset.timestamp = timestamp.getTime();

    const dateString = formatPinnedDate(timestamp);
    const timeString = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const dateClass = getDateClass(timestamp);
    const groupName = currentGroup ? currentGroup.name : `Group ${messageData.group_id}`;
    const truncatedGroupName = groupName.length > 16
        ? groupName.substring(0, 13) + '...'
        : groupName;

    pinnedItem.innerHTML = `
        <div class="pinned-date-indicator ${dateClass}">${dateString}</div>
        <div class="pinned-header">
            <span class="pinned-group-name">${currentGroup ? truncatedGroupName : `Group ${messageData.group_id}`}</span>
        </div>
        <div class="pinned-content">${messageData.content}</div>
        <div class="pinned-footer">
            <small>From: ${messageElement.querySelector('.message-sender').textContent}</small>
            <button class="unpin-btn" title="Unpin message" onclick="event.stopPropagation(); togglePinMessage(${messageData.id})">
                <i class="fas fa-thumbtack"></i>
            </button>
            <span class="pinned-time">${timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
    `;

    pinnedItem.addEventListener('click', (e) => {
        if (!e.target.classList.contains('unpin-btn')) {
            // Add a small delay to ensure group is loaded
            setTimeout(() => {
                navigateToPinnedMessage(messageData.group_id, messageData.id);
            }, 300);
        }
    });

    insertPinnedMessageInOrder(pinnedItem, pinnedList);
}
function insertPinnedMessageInOrder(newPinnedItem, pinnedList) {
    const newTimestamp = parseInt(newPinnedItem.dataset.timestamp);
    const pinnedItems = Array.from(pinnedList.children);

    // Find the position where the new item should be inserted
    let insertBefore = null;
    for (const item of pinnedItems) {
        const itemTimestamp = parseInt(item.dataset.timestamp);
        if (newTimestamp > itemTimestamp) {
            insertBefore = item;
            break;
        }
    }

    if (insertBefore) {
        pinnedList.insertBefore(newPinnedItem, insertBefore);
    } else {
        pinnedList.appendChild(newPinnedItem);
    }
}

function formatPinnedDate(date) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const inputDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (inputDate.getTime() === today.getTime()) {
        return 'Today';
    } else if (inputDate.getTime() === yesterday.getTime()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
}

function getDateClass(date) {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const inputDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (inputDate.getTime() === today.getTime()) {
        return 'today';
    } else if (inputDate.getTime() === yesterday.getTime()) {
        return 'yesterday';
    } else {
        return 'older';
    }
}

function navigateToPinnedMessage(groupId, messageId) {
    // First, check if we're already in the correct group
    if (currentGroup && currentGroup.id === groupId) {
        // We're in the right group, just find and highlight the message
        const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
        if (messageElement) {
            highlightAndScrollToMessage(messageElement);
            return;
        }
        
        // Message not found in current view, try to load it
        loadAndHighlightMessage(groupId, messageId);
        return;
    }
function loadAndHighlightMessage(groupId, messageId) {
    fetch(`/messages/${messageId}`)
        .then(response => {
            if (!response.ok) throw new Error('Message not found');
            return response.json();
        })
        .then(message => {
            if (message.group_id !== groupId) {
                throw new Error('Message not in this group');
            }
            
            // Add the message to the chat if it's not already there
            if (!document.querySelector(`.message[data-message-id="${messageId}"]`)) {
                addMessageToChat(message, initialLoad ? 'append' : 'prepend');
            }
            
            // Now try to find and highlight it
            const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
            if (messageElement) {
                highlightAndScrollToMessage(messageElement);
            } else {
                throw new Error('Could not display message');
            }
        })
        .catch(error => {
            console.error('Error loading message:', error);
            notificationManager.notify('error', 'Error', 'Could not load the pinned message');
        });
}

function highlightAndScrollToMessage(messageElement) {
    // Remove any existing highlights first
    document.querySelectorAll('.message.highlight').forEach(el => {
        el.classList.remove('highlight');
    });

    // Add highlight class
    messageElement.classList.add('highlight');

    // Calculate scroll position with some offset
    const messagesContainer = document.getElementById('messages');
    const messageRect = messageElement.getBoundingClientRect();
    const containerRect = messagesContainer.getBoundingClientRect();
    const scrollPosition = messageElement.offsetTop - containerRect.top - 100;

    // Scroll to message
    messagesContainer.scrollTo({
        top: scrollPosition,
        behavior: 'smooth'
    });

    // Remove highlight after animation completes
    setTimeout(() => {
        messageElement.classList.remove('highlight');
    }, 3000);
}
    // We need to switch groups first
    const groupItem = document.querySelector(`.group-item[data-group-id="${groupId}"]`);
    if (groupItem) {
        // Click the group to select it
        groupItem.click();

        // Wait for messages to load, then find and highlight the message
        const checkForMessage = () => {
            const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
            if (messageElement) {
                highlightAndScrollToMessage(messageElement);
            } else {
                // Message not found in loaded messages, try to fetch it specifically
                setTimeout(() => {
                    loadAndHighlightMessage(groupId, messageId);
                }, 500);
            }
        };

        // Start checking for the message
        setTimeout(checkForMessage, 300);
    } else {
        notificationManager.notify('error', 'Navigation Error', 'Could not find the group for this pinned message');
    }
}

function handleMessagePinned(data) {
    const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
    if (messageElement) {
        if (data.pinned) {
            messageElement.classList.add('pinned');
            addToPinnedMessages({
                id: data.message_id,
                group_id: data.group_id,
                content: messageElement.querySelector('.message-content').textContent,
                created_at: data.pinned_at || new Date().toISOString(),
                sender_id: data.sender_id,
                pinned_by: data.pinned_by
            });
            notificationManager.notify('success', 'Message Pinned', 'Message has been pinned to the group');
        } else {
            messageElement.classList.remove('pinned');
            removeFromPinnedMessages(data.message_id);
            notificationManager.notify('success', 'Message Unpinned', 'Message has been unpinned');
        }
    }
}
function sortPinnedMessages() {
    const pinnedList = document.querySelector('.pinned-list');
    if (!pinnedList) return;

    const pinnedItems = Array.from(pinnedList.children);

    // Sort by timestamp (newest first)
    pinnedItems.sort((a, b) => {
        return parseInt(b.dataset.timestamp) - parseInt(a.dataset.timestamp);
    });

    // Re-append in sorted order
    pinnedItems.forEach(item => pinnedList.appendChild(item));
}
function removeFromPinnedMessages(messageId) {
    const pinnedItem = document.querySelector(`.pinned-message[data-message-id="${messageId}"]`);
    if (pinnedItem) {
        pinnedItem.remove();
    }
}

function highlightMentions(content) {
    // Store mentions with user data
    const mentions = {};
    
    // Replace mentions with styled spans
    return content.replace(/@(\w+)/g, (match, username) => {
        const user = allUsers.find(u => u.username === username);
        if (user) {
            mentions[username] = user;
            return `<span class="mention" data-user-id="${user.id}">${match}</span>`;
        }
        return match;
    });
}

async function addMessageToChat(messageData, position = 'append') {
    // Handle voice messages separately
    if (messageData.message_type === "voice") {
        const messageElement = await createVoiceMessageElement(messageData);
        if (position === 'prepend') {
            messages.insertBefore(messageElement, messages.firstChild);
        } else {
            messages.appendChild(messageElement);
        }
        return;
    }

    const messageDate = new Date(messageData.created_at);
    const currentDate = new Date();

    // Determine date label
    // Determine date label
    let dateLabel = '';
    const messageDay = messageDate.toDateString();

    if (messageDay === currentDate.toDateString()) {
        dateLabel = 'Today';
    } else {
        const yesterday = new Date(currentDate);
        yesterday.setDate(yesterday.getDate() - 1);

        if (messageDay === yesterday.toDateString()) {
            dateLabel = 'Yesterday';
        } else {
            dateLabel = messageDate.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
        }
    }

    // Add date separator if needed
    if (!lastMessageDate || lastMessageDate !== dateLabel) {
        const dateSeparator = document.createElement('div');
        dateSeparator.className = 'date-separator';
        dateSeparator.textContent = dateLabel;
        
        if (position === 'prepend') {
            messages.insertBefore(dateSeparator, messages.firstChild);
        } else {
            messages.appendChild(dateSeparator);
        }
        
        lastMessageDate = dateLabel;
    }

    const isCurrentUser = messageData.sender_id === currentUser.id;
    const sender = allUsers.find(u => u.id === messageData.sender_id);
    const user = await fetchUser(messageData.sender_id);
    const senderName = user.name;

    const messageElement = document.createElement('div');
    messageElement.className = `message ${isCurrentUser ? 'sent' : 'received'} ${messageData.pinned ? 'pinned' : ''}`;
    messageElement.dataset.messageId = messageData.id;
    messageElement.dataset.messageType = messageData.message_type || "text";

    let replyContent = '';
    let replySender = '';
    if (messageData.reply_to_id) {
        const repliedMessage = await getMessageDetails(messageData.reply_to_id);
        if (repliedMessage) {
            replySender = repliedMessage.sender ? repliedMessage.sender.name : 'Unknown';
            replyContent = repliedMessage.message_type === 'voice' ? 
                '🎙️ Voice Message' : 
                (repliedMessage.content || '[Message]');
        }
    }

    let messageContent = messageData.content;
    if (messageData.is_deleted) {
        messageContent = '<i>Message deleted</i>';
    }

    if (messageData.mentions && messageData.mentions.includes(currentUser.id)) {
        messageContent = highlightMentions(messageContent);
        messageElement.classList.add('mentioned');
    }

    messageElement.innerHTML = `
        <div class="message-header">
            <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(senderName)}&background=random" alt="${senderName}" class="message-avatar">
            <span class="message-sender">${senderName}</span>
            <span class="message-action" onclick="togglePinMessage(${messageData.id})">
                <i class="fas fa-thumbtack ${isCurrentUser ? 'white-icon' : ''} ${messageData.pinned ? 'active' : ''}"></i>
            </span>
        </div>

        ${messageData.reply_to_id ? `
        <div class="message-reply" onclick="navigateToRepliedMessage(event, ${messageData.reply_to_id})">
            <div class="reply-header">
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(replySender)}&background=random"
                     alt="${replySender}" class="tooltip-avatar">
                <div class="message-reply-sender">${replySender}</div>
            </div>
            <div class="message-reply-content">${replyContent}</div>
        </div>` : ''}

        <div class="message-content">${messageContent}</div>

        <div class="message-reactions"></div>

        <div class="message-info ${isCurrentUser ? 'sent' : 'received'}">
            <span class="message-time">
                ${new Date(messageData.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                ${messageData.edited_at ? '<span>(edited)</span>' : ''}
            </span>
            ${messageData.pinned ? `<span class="pinned-indicator"><i class="fas fa-thumbtack"></i> Pinned ${formatPinnedDate(new Date(messageData.pinned_at))}</span>` : ''}
        </div>

        <div class="message-actions ${isCurrentUser ? 'sent' : 'received'}">
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '👍')">👍</span>
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '❤️')">❤️</span>
            <span class="message-action" onclick="reactToMessage(${messageData.id}, '😂')">😂</span>
            <button class="action-btn reply-btn" title="Reply" onclick="prepareReply(${messageData.id}, '${senderName}')">
                <i class="fas fa-reply"></i>
            </button>
            ${isCurrentUser ? `
                <button class="action-btn edit-btn" title="Edit message" onclick="editMessage(${messageData.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete-btn" title="Delete message" onclick="deleteMessage(${messageData.id}, true)">
                    <i class="fas fa-trash"></i>
                </button>
            ` : ''}
        </div>
    `;

    // Render grouped reactions with tooltip and count
    if (messageData.reactions && messageData.reactions.length > 0) {
        const reactionsContainer = messageElement.querySelector('.message-reactions');

        const reactionsByEmoji = {};
        messageData.reactions.forEach(reaction => {
            if (!reactionsByEmoji[reaction.emoji]) {
                reactionsByEmoji[reaction.emoji] = [];
            }
            reactionsByEmoji[reaction.emoji].push(reaction);
        });

        for (const [emoji, reactions] of Object.entries(reactionsByEmoji)) {
            const reactionElement = document.createElement('div');
            reactionElement.className = 'reaction-container';

            const emojiElement = document.createElement('span');
            emojiElement.className = 'reaction-emoji';
            emojiElement.textContent = emoji;
            emojiElement.onclick = (e) => {
                e.stopPropagation();
                reactToMessage(messageData.id, emoji);
            };

            const countElement = document.createElement('span');
            countElement.className = 'reaction-count';
            countElement.textContent = reactions.length;

            const tooltip = document.createElement('div');
            tooltip.className = 'reaction-tooltip';
            tooltip.innerHTML = reactions.map(r =>
                `<div class="tooltip-user">
                    <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(r.user.name)}&background=random"
                         alt="${r.user.name}" class="tooltip-avatar">
                    <span>${r.user.name}</span>
                </div>`
            ).join('');

            reactionElement.appendChild(emojiElement);
            reactionElement.appendChild(countElement);
            reactionElement.appendChild(tooltip);

            if (reactions.some(r => r.user_id === currentUser.id)) {
                reactionElement.classList.add('user-reacted');
            }

            reactionsContainer.appendChild(reactionElement);
        }
    }

    if (position === 'prepend') {
        messages.insertBefore(messageElement, messages.firstChild);
    } else {
        messages.appendChild(messageElement);
    }
}

function highlightMentions(content) {
    return content.replace(/@(\w+)/g, (match, username) => {
        const user = allUsers.find(u => u.username === username);
        if (user && user.id === currentUser.id) {
            return `<span class="mention">${match}</span>`;
        }
        return match;
    });
}

function prepareReply(messageId, senderName) {
    // Find the message element in the DOM
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageElement) return;

    // Get the message content (handle deleted messages and voice messages)
    const isVoiceMessage = messageElement.dataset.messageType === "voice";
    let messageContent = isVoiceMessage ? 
        "🎙️ Voice Message" : 
        (messageElement.querySelector('.message-content')?.textContent || '[Message]');
    
    if (messageElement.classList.contains('deleted')) {
        messageContent = "[Deleted Message]";
    }

    // Remove any existing reply indicator
    cancelReply();

    // Create reply indicator
    const replyIndicator = document.createElement('div');
    replyIndicator.className = 'reply-indicator';
    replyIndicator.dataset.messageId = messageId;

    replyIndicator.innerHTML = `
        <div class="reply-header">
            <span class="reply-sender">Replying to ${senderName}</span>
            <button class="cancel-reply-btn" onclick="cancelReply(event)">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="reply-content">${messageContent}</div>
    `;

    // Add click handler to scroll to original message
    replyIndicator.addEventListener('click', (e) => {
        if (!e.target.classList.contains('cancel-reply-btn')) {
            navigateToRepliedMessage(e, messageId);
        }
    });

    // Get the message input container
    const messageInputContainer = document.querySelector('.message-input');

    // Insert the reply indicator before the message input
    messageInputContainer.parentNode.insertBefore(replyIndicator, messageInputContainer);

    // Focus the input field
    messageInput.focus();

    // Store the message ID we're replying to
    messageInput.dataset.replyTo = messageId;
}

function cancelReply(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const replyIndicator = document.querySelector('.reply-indicator');
    if (replyIndicator) {
        replyIndicator.remove();
    }
    delete messageInput.dataset.replyTo;
}

function replyNavigateToMessage(messageId) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (messageElement) {
        // Highlight the message
        messageElement.classList.add('highlight');

        // Scroll to message
        messageElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });

        // Remove highlight after delay
        setTimeout(() => {
            messageElement.classList.remove('highlight');
        }, 3000);
    }
}

function handleReactionsUpdated(data) {
    const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
    if (!messageElement) return;

    let reactionsContainer = messageElement.querySelector('.message-reactions');
    if (!reactionsContainer) {
        reactionsContainer = document.createElement('div');
        reactionsContainer.className = 'message-reactions';
        messageElement.insertBefore(reactionsContainer, messageElement.querySelector('.message-info'));
    }

    // Clear existing reactions
    reactionsContainer.innerHTML = '';

    // If no reactions, we're done
    if (!data.reactions || data.reactions.length === 0) return;

    // Group reactions by emoji with user info
    const reactionsByEmoji = {};
    data.reactions.forEach(reaction => {
        if (!reactionsByEmoji[reaction.emoji]) {
            reactionsByEmoji[reaction.emoji] = {
                count: 0,
                users: []
            };
        }
        reactionsByEmoji[reaction.emoji].count++;
        reactionsByEmoji[reaction.emoji].users.push(reaction.user);
    });

    // Create new reaction elements
    for (const [emoji, reactionData] of Object.entries(reactionsByEmoji)) {
        const reactionElement = document.createElement('div');
        reactionElement.className = 'reaction-container';

        // Highlight if current user reacted
        if (reactionData.users.some(user => user.id === currentUser.id)) {
            reactionElement.classList.add('user-reacted');
        }

        const emojiElement = document.createElement('span');
        emojiElement.className = 'reaction-emoji';
        emojiElement.textContent = emoji;
        emojiElement.onclick = (e) => {
            e.stopPropagation();
            reactToMessage(data.message_id, emoji);
        };

        const countElement = document.createElement('span');
        countElement.className = 'reaction-count';
        countElement.textContent = reactionData.count;

        // Tooltip with user names
        const tooltip = document.createElement('div');
        tooltip.className = 'reaction-tooltip';
        tooltip.innerHTML = reactionData.users.map(user =>
            `<div class="tooltip-user">
                <img src="${`https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`}" 
                     alt="${user.name}" class="tooltip-avatar">
                <span>${user.name}</span>
            </div>`
        ).join('');

        reactionElement.appendChild(emojiElement);
        reactionElement.appendChild(countElement);
        reactionElement.appendChild(tooltip);

        reactionsContainer.appendChild(reactionElement);
    }
}
// Helper function to get the sender name of a replied message
function getRepliedMessageSender(messageId, messageData = null) {
    // Try to find the message in the DOM first
    const repliedMessage = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (repliedMessage) {
        return repliedMessage.querySelector('.message-sender').textContent;
    }

    // If we have messageData with sender info, use that
    if (messageData && messageData.reply_to_sender_id) {
        const sender = allUsers.find(u => u.id === messageData.reply_to_sender_id);
        return sender ? sender.name : 'user';
    }

    return 'message';
}

async function getMessageReplyContent(messageId) {
    // First try to find the message in the DOM
    const repliedMessage = document.querySelector(`.message[data-message-id="${messageId}"]`);
    
    if (repliedMessage) {
        // Handle different message types
        if (repliedMessage.dataset.messageType === "voice") {
            return "🎙️ Voice Message";
        }
        
        const contentElement = repliedMessage.querySelector('.message-content');
        return contentElement ? 
            (contentElement.textContent.length > 50 ? 
                contentElement.textContent.substring(0, 50) + '...' : 
                contentElement.textContent) :
            '[Message]';
    }

    // If not found in DOM, fetch it from the server
    try {
        const response = await fetch(`/messages/${messageId}`);
        if (!response.ok) throw new Error('Message not found');
        const message = await response.json();
        
        // Handle different message types from server
        if (message.message_type === "voice") {
            return "🎙️ Voice Message";
        }
        
        return message.content.length > 50 ?
            message.content.substring(0, 50) + '...' :
            message.content;
    } catch (error) {
        console.error('Error fetching replied message:', error);
        return '[Message not available]';
    }
}

function navigateToRepliedMessage(event, messageId) {
    event.stopPropagation();

    // Find the message element in the DOM
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (messageElement) {
        // Highlight the message
        messageElement.classList.add('highlight');

        // Scroll to message
        messageElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });

        // Remove highlight after delay
        setTimeout(() => {
            messageElement.classList.remove('highlight');
        }, 3000);
    } else {
        // If message isn't loaded, try to find which group it's in
        // This would require additional backend support to get the group ID
        notificationManager.notify('info', 'Message Not Loaded', 'The original message is not currently loaded');
    }
}

function editMessage(messageId) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    const currentContent = messageElement.querySelector('.message-content').textContent;

    // Create edit textarea
    const editInput = document.createElement('textarea');
    editInput.className = 'message-edit-input';
    editInput.value = currentContent;

    // Replace content with input
    messageElement.querySelector('.message-content').replaceWith(editInput);
    editInput.focus();

    const saveEdit = () => {
        const newContent = editInput.value.trim();
        if (newContent && newContent !== currentContent) {
            const message = {
                type: 'edit_message',
                data: {
                    message_id: messageId,
                    new_content: newContent
                }
            };
            socket.send(JSON.stringify(message));
        }
        // Restore original content if empty or same
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = newContent || currentContent;
        editInput.replaceWith(contentElement);
    };

    editInput.addEventListener('blur', saveEdit);
    editInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            saveEdit();
        }
    });
}

function handleMessageUpdated(messageData) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageData.id}"]`);
    if (messageElement) {
        messageElement.querySelector('.message-content').textContent = messageData.content;
        messageElement.querySelector('.message-info').innerHTML = `
            <span>${new Date(messageData.created_at).toLocaleTimeString()}</span>
            <span>(edited)</span>
        `;
    }
}
// Edit Message Function
function setupEditMessage(messageId, currentContent) {
    const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
    const contentElement = messageElement.querySelector('.message-content');

    // Create edit input
    const editInput = document.createElement('textarea');
    editInput.className = 'message-edit-input';
    editInput.value = currentContent;

    // Replace content with input
    contentElement.replaceWith(editInput);
    editInput.focus();

    // Save on Enter or blur
    const saveEdit = () => {
        const newContent = editInput.value.trim();
        if (newContent && newContent !== currentContent) {
            fetch(`/messages/${messageId}?user_id=${currentUser.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: newContent })
            })
                .then(response => {
                    if (!response.ok) throw new Error('Failed to update message');
                    return response.json();
                })
                .then(updatedMessage => {
                    // Replace input with updated content
                    const newContentElement = document.createElement('div');
                    newContentElement.className = 'message-content';
                    newContentElement.textContent = updatedMessage.content;

                    // Add edited indicator
                    const timeElement = messageElement.querySelector('.message-time');
                    if (timeElement) {
                        timeElement.innerHTML += ' <span>(edited)</span>';
                    }

                    editInput.replaceWith(newContentElement);
                    notificationManager.notify('success', 'Message Updated', 'Your message has been updated');
                })
                .catch(error => {
                    notificationManager.notify('error', 'Update Failed', error.message);
                    // Restore original content
                    const originalContent = document.createElement('div');
                    originalContent.className = 'message-content';
                    originalContent.textContent = currentContent;
                    editInput.replaceWith(originalContent);
                });
        } else {
            // Restore original content
            const originalContent = document.createElement('div');
            originalContent.className = 'message-content';
            originalContent.textContent = currentContent;
            editInput.replaceWith(originalContent);
        }
    };

    editInput.addEventListener('blur', saveEdit);
    editInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            saveEdit();
        }
    });
}

// Delete Message Function
function setupDeleteMessage(messageId) {
    if (confirm('Are you sure you want to delete this message?')) {
        fetch(`/messages/${messageId}?user_id=${currentUser.id}`, {
            method: 'DELETE'
        })
            .then(response => {
                if (!response.ok) throw new Error('Failed to delete message');
                return response.json();
            })
            .then(() => {
                const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
                messageElement.remove();
                notificationManager.notify('success', 'Message Deleted', 'Your message has been deleted');
            })
            .catch(error => {
                notificationManager.notify('error', 'Deletion Failed', error.message);
            });
    }
}
function deleteMessage(messageId, forAll = false) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        notificationManager.notify('error', 'Connection Error', 'Not connected to server');
        return;
    }

    const message = {
        type: 'delete_message',
        data: {
            message_id: messageId,
            for_all: forAll
        }
    };
    socket.send(JSON.stringify(message));
}

function handleMessageDeleted(data) {
    const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
    if (messageElement) {
        if (data.for_all) {
            // Soft delete - show "message deleted"
            if (messageElement.dataset.messageType === "voice") {
                messageElement.classList.add('deleted');
                const voiceMessage = messageElement.querySelector('.voice-message');
                if (voiceMessage) {
                    voiceMessage.innerHTML = '<i class="fas fa-microphone-slash"></i> <span class="deleted-text">Voice message deleted</span>';
                }
            } else {
                messageElement.querySelector('.message-content').innerHTML = '<i>Message deleted</i>';
            }
            
            // Remove action buttons except for reply
            const actions = messageElement.querySelector('.message-actions');
            if (actions) {
                actions.innerHTML = `
                    <button class="action-btn reply-btn" title="Reply" onclick="prepareReply(${data.message_id}, 'Deleted User')">
                        <i class="fas fa-reply"></i>
                    </button>
                `;
            }
        } else {
            // Hard delete - remove completely
            messageElement.remove();
        }
    }
}

function pinMessage(messageId, pin = true) {
    const message = {
        type: 'pin_message',
        data: {
            message_id: messageId,
            pin: pin
        }
    };
    socket.send(JSON.stringify(message));
}

function reactToMessage(messageId, emoji) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        notificationManager.notify('error', 'Connection Error', 'Not connected to server');
        return;
    }

    const message = {
        type: 'add_reaction',
        data: {
            message_id: messageId,
            emoji: emoji
        }
    };
    socket.send(JSON.stringify(message));
}

function handleReactionChange(data) {
    const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
    if (!messageElement) return;

    let reactionsContainer = messageElement.querySelector('.message-reactions');
    if (!reactionsContainer) {
        reactionsContainer = document.createElement('div');
        reactionsContainer.className = 'message-reactions';
        messageElement.insertBefore(reactionsContainer, messageElement.querySelector('.message-info'));
    }

    // Clear existing reactions
    reactionsContainer.innerHTML = '';

    // Group reactions by emoji
    const reactionsByEmoji = {};
    data.reactions.forEach(reaction => {
        if (!reactionsByEmoji[reaction.emoji]) {
            reactionsByEmoji[reaction.emoji] = [];
        }
        reactionsByEmoji[reaction.emoji].push(reaction);
    });

    // Create new reaction elements
    for (const [emoji, reactions] of Object.entries(reactionsByEmoji)) {
        const reactionElement = document.createElement('div');
        reactionElement.className = 'reaction-container';

        // Add 'user-reacted' class if current user has this reaction
        if (reactions.some(r => r.user_id === currentUser.id)) {
            reactionElement.classList.add('user-reacted');
        }

        const emojiElement = document.createElement('span');
        emojiElement.className = 'reaction-emoji';
        emojiElement.textContent = emoji;
        emojiElement.onclick = (e) => {
            e.stopPropagation();
            reactToMessage(data.message_id, emoji);
        };

        const countElement = document.createElement('span');
        countElement.className = 'reaction-count';
        countElement.textContent = reactions.length;

        const tooltip = document.createElement('div');
        tooltip.className = 'reaction-tooltip';
        tooltip.innerHTML = reactions.map(r =>
            `<div class="tooltip-user">
                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(r.user_name)}&background=random"
                     alt="${r.user_name}" class="tooltip-avatar">
                <span>${r.user_name}</span>
            </div>`
        ).join('');

        reactionElement.appendChild(emojiElement);
        reactionElement.appendChild(countElement);
        reactionElement.appendChild(tooltip);

        reactionsContainer.appendChild(reactionElement);
    }
}

function handleReactionAdded(reactionData) {
    const messageElement = document.querySelector(`.message[data-message-id="${reactionData.message_id}"]`);
    if (!messageElement) return;

    let reactionsContainer = messageElement.querySelector('.message-reactions');
    if (!reactionsContainer) {
        reactionsContainer = document.createElement('div');
        reactionsContainer.className = 'message-reactions';
        messageElement.insertBefore(reactionsContainer, messageElement.querySelector('.message-info'));
    }

    // Find existing reaction for this emoji
    const existingReaction = Array.from(reactionsContainer.querySelectorAll('.reaction-container'))
        .find(el => el.querySelector('.reaction-emoji').textContent === reactionData.emoji);

    if (existingReaction) {
        // Update count
        const countElement = existingReaction.querySelector('.reaction-count');
        countElement.textContent = parseInt(countElement.textContent) + 1;

        // Add user to tooltip
        const tooltip = existingReaction.querySelector('.reaction-tooltip');
        tooltip.innerHTML += `
            <div class="tooltip-user">
                <img src="${`https://ui-avatars.com/api/?name=${encodeURIComponent(reactionData.user.name)}&background=random`}" 
                     alt="${reactionData.user.name}" class="tooltip-avatar">
                <span>${reactionData.user.name}</span>
            </div>
        `;

        // Highlight if current user reacted
        if (reactionData.user_id === currentUser.id) {
            existingReaction.classList.add('user-reacted');
        }
    } else {
        // Create new reaction element
        const reactionElement = document.createElement('div');
        reactionElement.className = 'reaction-container';

        const emojiElement = document.createElement('span');
        emojiElement.className = 'reaction-emoji';
        emojiElement.textContent = reactionData.emoji;
        emojiElement.onclick = (e) => {
            e.stopPropagation();
            reactToMessage(reactionData.message_id, reactionData.emoji);
        };

        const countElement = document.createElement('span');
        countElement.className = 'reaction-count';
        countElement.textContent = '1';

        const tooltip = document.createElement('div');
        tooltip.className = 'reaction-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-user">
                <img src="${`https://ui-avatars.com/api/?name=${encodeURIComponent(reactionData.user.name)}&background=random`}" 
                     alt="${reactionData.user.name}" class="tooltip-avatar">
                <span>${reactionData.user.name}</span>
            </div>
        `;

        reactionElement.appendChild(emojiElement);
        reactionElement.appendChild(countElement);
        reactionElement.appendChild(tooltip);

        // Highlight if current user reacted
        if (reactionData.user_id === currentUser.id) {
            reactionElement.classList.add('user-reacted');
        }

        reactionsContainer.appendChild(reactionElement);
    }
}

function handleReactionRemoved(data) {
    const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
    if (!messageElement) return;

    const reactionsContainer = messageElement.querySelector('.message-reactions');
    if (!reactionsContainer) return;

    // Find the reaction container for this emoji
    const reactionContainer = Array.from(reactionsContainer.querySelectorAll('.reaction-container'))
        .find(el => el.querySelector('.reaction-emoji').textContent === data.emoji);

    if (reactionContainer) {
        const countElement = reactionContainer.querySelector('.reaction-count');
        const newCount = parseInt(countElement.textContent) - 1;

        if (newCount <= 0) {
            reactionContainer.remove();
        } else {
            countElement.textContent = newCount;

            // Remove user from tooltip
            const tooltip = reactionContainer.querySelector('.reaction-tooltip');
            const userElements = tooltip.querySelectorAll('.tooltip-user');
            for (const userElement of userElements) {
                if (userElement.textContent.includes(data.user_name)) {
                    userElement.remove();
                    break;
                }
            }

            // Remove highlight if current user unreacted
            if (data.user_id === currentUser.id) {
                reactionContainer.classList.remove('user-reacted');
            }
        }
    }
}

function handleOnlineUsersUpdate(data) {
    if (currentGroup && data.group_id === currentGroup.id) {
        updateOnlineUsers(data.users);
    }
}

function updateOnlineUsers(userIds) {
    groupMembers.innerHTML = '';
    const onlineUsers = new Set(userIds);
    const usersMap = new Map(allUsers.map(user => [user.id, user]));

    // Always show yourself first if you're in the group
    if (currentUser && onlineUsers.has(currentUser.id)) {
        const user = usersMap.get(currentUser.id);
        if (user) {
            const member = createMemberElement(user, true);
            groupMembers.appendChild(member);
        }
    }

    // Show other users
    userIds.forEach(userId => {
        if (userId === currentUser?.id) return; // Skip yourself (already added)

        const user = usersMap.get(userId);
        if (user) {
            const member = createMemberElement(user, true);
            groupMembers.appendChild(member);
        }
    });
}
function createMemberElement(user, isOnline) {
    const member = document.createElement('div');
    member.className = `member-avatar ${isOnline ? 'online' : 'offline'}`;
    member.title = `${user.username} ${isOnline ? '(online)' : '(offline)'}`;

    const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`;
    member.innerHTML = `
        <img src="${avatarUrl}" alt="${user.username}">
    `;
    return member;
}

function getOnlineUsers(groupId) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const message = {
            type: 'online_users',
            data: {
                group_id: groupId
            }
        };
        socket.send(JSON.stringify(message));
    }
}
async function createGroup() {
    // Get group name with validation
    let groupName;
    while (true) {
        groupName = prompt('Enter group name (3-50 characters):');
        if (groupName === null) return; // User cancelled
        if (groupName.length >= 3 && groupName.length <= 50) break;
        alert('Group name must be between 3 and 50 characters');
    }

    // Get optional description
    const groupDescription = prompt('Enter group description (optional, max 200 characters):') || '';

    // Prepare group data
    const groupData = {
        name: groupName.trim(),
        description: groupDescription.trim(),
        is_public: true
    };

    // Check WebSocket connection
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        notificationManager.notify('error', 'Connection Error', 'Not connected to server');
        return;
    }

    try {
        // Set loading state
        createGroupBtn.disabled = true;
        createGroupBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';

        // Create promise to handle the response
        const creationPromise = new Promise((resolve, reject) => {
            const handler = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'new_group') {
                        socket.removeEventListener('message', handler);
                        resolve(data.data);
                    } else if (data.type === 'error' && data.data.context === 'group_creation') {
                        socket.removeEventListener('message', handler);
                        reject(new Error(data.data.message));
                    }
                } catch (error) {
                    socket.removeEventListener('message', handler);
                    reject(error);
                }
            };

            socket.addEventListener('message', handler);

            // Set timeout in case server doesn't respond
            setTimeout(() => {
                socket.removeEventListener('message', handler);
                reject(new Error('Server timeout'));
            }, 10000);
        });

        // Send creation request
        socket.send(JSON.stringify({
            type: 'create_group',
            data: groupData
        }));

        // Wait for response
        const newGroup = await creationPromise;

        // Add to sidebar
        addGroupToSidebar(newGroup);

        // Automatically join the group
        await joinGroup(newGroup.id);

        // Select the group
        selectGroup(newGroup);

        notificationManager.notify('success', 'Group Created', `${newGroup.name} was successfully created`);

    } catch (error) {
        console.error('Group creation error:', error);
        notificationManager.notify('error', 'Creation Failed', error.message || 'Failed to create group');
    } finally {
        // Reset button state
        createGroupBtn.disabled = false;
        createGroupBtn.innerHTML = '<i class="fas fa-plus"></i> Create Group';
    }
}

// Add typing event listener to message input
messageInput.addEventListener('input', handleTyping);

function handleTyping() {
    if (!currentGroup) return;

    const is_typing = messageInput.value.length > 0;

    if (socket && socket.readyState === WebSocket.OPEN) {
        const message = {
            type: 'typing',
            data: {
                group_id: currentGroup.id,
                is_typing: is_typing
            }
        };
        socket.send(JSON.stringify(message));
    }
}

// Handle typing notifications
async function handleTypingNotification(data) {
    if (!currentGroup || data.group_id !== currentGroup.id) return;

    // Skip if this is the current user's typing notification
    if (data.user_id === currentUser?.id) return;

    const { user_id, is_typing } = data;
    let user_info;

    try {
        const response = await fetch(`/users/${user_id}`);
        if (response.ok) {
            const user_json = await response.json();
            user_info = {
                id: user_json.id,
                name: user_json.name,
                avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(user_json.name)}&background=random`
            };
        }
    } catch (error) {
        console.error('Failed to fetch user info:', error);
    }

    if (is_typing) {
        typingUsers[user_id] = user_info;
    } else {
        delete typingUsers[user_id];
    }

    updateTypingIndicator();
}

function updateTypingIndicator() {
    const typingContainer = document.getElementById('typingIndicator');
    const usersTyping = Object.values(typingUsers);

    // Remove indicator if no one is typing
    if (usersTyping.length === 0) {
        if (typingContainer) typingContainer.remove();
        return;
    }

    // Create or update container
    const container = typingContainer || document.createElement('div');
    container.id = 'typingIndicator';
    container.className = 'typing-indicator-container';
    container.innerHTML = '';

    // Add avatars (max 3)
    const usersToShow = usersTyping.slice(0, 3);
    usersToShow.forEach(user => {
        const avatar = document.createElement('img');
        avatar.className = 'typing-indicator-avatar';
        avatar.src = user.avatar;
        avatar.alt = user.name;
        container.appendChild(avatar);
    });

    // Add content with improved multiple user handling
    const content = document.createElement('div');
    content.className = 'typing-indicator-content';

    let namesText;
    if (usersTyping.length === 1) {
        namesText = `${usersTyping[0].name} is typing`;
    } else if (usersTyping.length === 2) {
        namesText = `${usersTyping[0].name} and ${usersTyping[1].name} are typing`;
    } else if (usersTyping.length === 3) {
        namesText = `${usersTyping[0].name}, ${usersTyping[1].name}, and ${usersTyping[2].name} are typing`;
    } else {
        namesText = `${usersTyping[0].name}, ${usersTyping[1].name}, and ${usersTyping.length - 2} others are typing`;
    }

    const nameElement = document.createElement('div');
    nameElement.className = 'typing-indicator-name';
    nameElement.textContent = namesText;
    content.appendChild(nameElement);

    const dots = document.createElement('div');
    dots.className = 'typing-indicator-dots';
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        dots.appendChild(dot);
    }
    content.appendChild(dots);

    container.appendChild(content);

    // Add to DOM if new element
    if (!typingContainer) {
        messages.appendChild(container);
    }

    scrollToBottom();
}
// Add this utility function to your script.js
function debounce(func, wait) {
    let timeout;
    return function () {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

// Update your typing event listener to use debounce
messageInput.addEventListener('input', debounce(handleTyping, 500));

// Also add a timeout to automatically stop typing indication after 3 seconds of inactivity
let typingTimeout;
messageInput.addEventListener('input', () => {
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        if (socket && socket.readyState === WebSocket.OPEN && currentGroup) {
            const message = {
                type: 'typing',
                data: {
                    group_id: currentGroup.id,
                    is_typing: false
                }
            };
            socket.send(JSON.stringify(message));
        }
    }, 3000);
});

// Add to message input event listeners
messageInput.addEventListener('input', function(e) {
    const cursorPos = e.target.selectionStart;
    const textBeforeCursor = e.target.value.substring(0, cursorPos);
    
    // Check if user is trying to mention someone
    const atSymbolIndex = textBeforeCursor.lastIndexOf('@');
    if (atSymbolIndex >= 0 && 
        (atSymbolIndex === 0 || textBeforeCursor[atSymbolIndex-1] === ' ')) {
        
        const searchTerm = textBeforeCursor.substring(atSymbolIndex + 1);
        showUserSuggestions(searchTerm, atSymbolIndex);
    } else {
        hideUserSuggestions();
    }
});

// Add these to your script.js

// Show registration modal
document.getElementById('registerBtn').addEventListener('click', () => {
    document.getElementById('registerModal').style.display = 'flex';
});

// Hide registration modal
document.getElementById('cancelRegisterBtn').addEventListener('click', () => {
    document.getElementById('registerModal').style.display = 'none';
});

// Handle registration submission
document.getElementById('submitRegisterBtn').addEventListener('click', async () => {
    const username = document.getElementById('registerUsername').value.trim();
    const name = document.getElementById('registerName').value.trim();
    const errorElement = document.getElementById('registerError');
    
    // Basic validation
    if (!username || !name ) {
        errorElement.textContent = 'Please fill in all required fields';
        errorElement.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch('/register/user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                name: name
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }
        const userData = await response.json();
        // Close modal and refresh user list
        document.getElementById('registerModal').style.display = 'none';
        authenticateUser(userData.username)
    } catch (error) {
        errorElement.textContent = error.message;
        errorElement.style.display = 'block';
        console.error('Registration error:', error);
    }
});

function showUserSuggestions(searchTerm, atPosition) {
    const filteredUsers = allUsers.filter(user => 
        user.name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    let suggestionBox = document.getElementById('userSuggestions'); // Changed to let
    if (!suggestionBox) {
        suggestionBox = document.createElement('div');
        suggestionBox.id = 'userSuggestions';
        document.body.appendChild(suggestionBox);
    }
    
    suggestionBox.innerHTML = filteredUsers.map(user => `
        <div class="user-suggestion" 
             data-username="${user.username}"
             onclick="insertMention('${user.username}')">
            <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random" 
                 alt="${user.name}" class="user-suggestion-avatar">
            <div class="user-suggestion-info">
                <div class="user-suggestion-name">${user.name}</div>
                <div class="user-suggestion-username">@${user.username}</div>
            </div>
        </div>
    `).join('');
    
    // Position the box near the @ symbol
    const inputRect = messageInput.getBoundingClientRect();
    suggestionBox.style.position = 'absolute';
    suggestionBox.style.left = `${inputRect.left + atPosition*8}px`;
    suggestionBox.style.top = `${inputRect.top - 230}px`;
    suggestionBox.style.display = 'block';
}

function insertMention(username) {
    const currentValue = messageInput.value;
    const cursorPos = messageInput.selectionStart;
    const atSymbolIndex = currentValue.lastIndexOf('@', cursorPos - 1);
    
    messageInput.value = 
        currentValue.substring(0, atSymbolIndex) + 
        `@${username} ` + 
        currentValue.substring(cursorPos);
    
    // Move cursor after the inserted mention
    messageInput.selectionStart = messageInput.selectionEnd = atSymbolIndex + username.length + 2;
    hideUserSuggestions();
}

function hideUserSuggestions() {
    const suggestionBox = document.getElementById('userSuggestions');
    if (suggestionBox) {
        suggestionBox.style.display = 'none';
    }
}



function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
}
document.addEventListener('DOMContentLoaded', init);