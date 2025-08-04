
document.addEventListener('DOMContentLoaded', () => {
    const appContainer = document.getElementById('app-container');

    const screens = {
        onboarding: `
            <div class="screen active" id="onboarding">
                <div style="text-align: center; padding-top: 48px; padding-bottom: 48px;">
                    <h2>Welcome to PathCraft</h2>
                    <p>Deconstruct your goals. Conquer your day.</p>
                    <div style="margin: 32px 0;">
                        <p style="font-size: 14px; color: var(--secondary-text);">Get Started &rarr; Choose Goals &rarr; Personalize</p>
                        <div style="width: 80%; margin: 8px auto; background: var(--border-color); border-radius: 4px; height: 4px;">
                            <div style="width: 33%; background: var(--accent); height: 4px; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <button class="btn btn-primary" data-target="dashboard">Next</button>
                </div>
            </div>
        `,
        dashboard: `
            <div class="screen" id="dashboard">
                <h2 style="margin-bottom: 24px;">Dashboard</h2>
                <div class="bento-grid">
                    <div class="card" style="grid-column: span 2;">
                        <h3>Today's Goals</h3>
                        <p>[ ] Task 1</p>
                        <p>[ ] Task 2</p>
                    </div>
                    <div class="card">
                        <h3>Calendar</h3>
                        <p>Mon 12</p>
                    </div>
                    <div class="card">
                        <h3>AI Suggestion</h3>
                        <p>You're most productive in the mornings.</p>
                    </div>
                </div>
                 <button class="btn btn-secondary" style="margin-top: 24px;" data-target="goal-details">View Goal</button>
            </div>
        `,
        goalDetails: `
            <div class="screen" id="goal-details">
                <h2 style="margin-bottom: 24px;">Launch New Website</h2>
                <p>Progress: 75%</p>
                <div style="width: 100%; background: var(--border-color); border-radius: 4px; height: 8px; margin-bottom: 24px;">
                    <div style="width: 75%; background: var(--success); height: 8px; border-radius: 4px;"></div>
                </div>
                <h3>Sub-Tasks</h3>
                <p>[✓] Phase 1: Research</p>
                <p>[ ] Phase 2: Development</p>
                <button class="btn btn-secondary" style="margin-top: 24px;" data-target="task-details">View Task</button>
            </div>
        `,
        taskDetails: `
            <div class="screen" id="task-details">
                <h2 style="margin-bottom: 24px;">Develop Backend API</h2>
                <p><strong>Due Date:</strong> Oct 28, 2025</p>
                <p><strong>Priority:</strong> High</p>
                <h3>Checklist</h3>
                <p>[ ] Set up database schema</p>
                <p>[ ] Create user authentication</p>
                <button class="btn btn-primary" style="margin-top: 24px;" data-target="dashboard">Mark as Complete</button>
            </div>
        `
    };

    // Initial render
    appContainer.innerHTML = screens.onboarding + screens.dashboard + screens.goalDetails + screens.taskDetails;

    appContainer.addEventListener('click', (e) => {
        if (e.target.matches('[data-target]')) {
            const targetId = e.target.dataset.target;
            
            // Hide all screens
            appContainer.querySelectorAll('.screen').forEach(screen => {
                screen.classList.remove('active');
            });

            // Show the target screen
            const targetScreen = document.getElementById(targetId);
            if (targetScreen) {
                targetScreen.classList.add('active');
            }
        }
    });
});
