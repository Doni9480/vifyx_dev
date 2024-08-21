
function init_user_status() {
    const locking = async (pk) => {
        fetch()
        return true;
    };
    const unlocking = (pk) => {
        // Implement unlocking logic here
        return true;
    };
    const user_statuses = {
        'locked': locking,
        'unlocked': unlocking
    };
}