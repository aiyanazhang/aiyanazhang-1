(function() {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreElement = document.getElementById('score');
    
    const gridSize = 20;
    const cellSize = canvas.width / gridSize;
    
    let snake = [
        { x: 10, y: 10 },
        { x: 9, y: 10 },
        { x: 8, y: 10 }
    ];
    
    let direction = 'right';
    let food = generateFood();
    let score = 0;
    let gameInterval;
    
    function generateFood() {
        let newFood;
        do {
            newFood = {
                x: Math.floor(Math.random() * gridSize),
                y: Math.floor(Math.random() * gridSize)
            };
        } while (isOnSnake(newFood));
        return newFood;
    }
    
    function isOnSnake(pos) {
        return snake.some(segment => segment.x === pos.x && segment.y === pos.y);
    }
    
    function getNextPosition(head, dir) {
        const newHead = { ...head };
        switch(dir) {
            case 'right': newHead.x++; break;
            case 'left': newHead.x--; break;
            case 'up': newHead.y--; break;
            case 'down': newHead.y++; break;
        }
        return newHead;
    }
    
    function isValidMove(pos) {
        if (pos.x < 0 || pos.x >= gridSize || pos.y < 0 || pos.y >= gridSize) {
            return false;
        }
        if (snake.slice(1).some(segment => segment.x === pos.x && segment.y === pos.y)) {
            return false;
        }
        return true;
    }
    
    function findSafeDirection() {
        const head = snake[0];
        const directions = ['right', 'left', 'up', 'down'];
        
        const opposites = {
            'right': 'left',
            'left': 'right',
            'up': 'down',
            'down': 'up'
        };
        
        const validDirections = directions.filter(dir => {
            if (dir === opposites[direction]) return false;
            const nextPos = getNextPosition(head, dir);
            return isValidMove(nextPos);
        });
        
        if (validDirections.length === 0) {
            return direction;
        }
        
        const towardsFood = validDirections.find(dir => {
            const nextPos = getNextPosition(head, dir);
            const currentDist = Math.abs(head.x - food.x) + Math.abs(head.y - food.y);
            const nextDist = Math.abs(nextPos.x - food.x) + Math.abs(nextPos.y - food.y);
            return nextDist < currentDist;
        });
        
        if (towardsFood) {
            return towardsFood;
        }
        
        return validDirections[Math.floor(Math.random() * validDirections.length)];
    }
    
    function update() {
        direction = findSafeDirection();
        
        const head = snake[0];
        const newHead = getNextPosition(head, direction);
        
        if (!isValidMove(newHead)) {
            resetGame();
            return;
        }
        
        snake.unshift(newHead);
        
        if (newHead.x === food.x && newHead.y === food.y) {
            score += 10;
            scoreElement.textContent = score;
            food = generateFood();
        } else {
            snake.pop();
        }
    }
    
    function resetGame() {
        snake = [
            { x: 10, y: 10 },
            { x: 9, y: 10 },
            { x: 8, y: 10 }
        ];
        direction = 'right';
        score = 0;
        scoreElement.textContent = score;
        food = generateFood();
    }
    
    function drawGrid() {
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= gridSize; i++) {
            ctx.beginPath();
            ctx.moveTo(i * cellSize, 0);
            ctx.lineTo(i * cellSize, canvas.height);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(0, i * cellSize);
            ctx.lineTo(canvas.width, i * cellSize);
            ctx.stroke();
        }
    }
    
    function drawFood() {
        ctx.fillStyle = '#FF5252';
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#FF5252';
        
        const x = food.x * cellSize + cellSize / 2;
        const y = food.y * cellSize + cellSize / 2;
        const radius = cellSize / 2.5;
        
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.shadowBlur = 0;
    }
    
    function drawSnake() {
        snake.forEach((segment, index) => {
            const opacity = 1 - (index / snake.length) * 0.3;
            
            if (index === 0) {
                ctx.fillStyle = '#66BB6A';
            } else {
                ctx.fillStyle = `rgba(76, 175, 80, ${opacity})`;
            }
            
            ctx.shadowBlur = index === 0 ? 8 : 0;
            ctx.shadowColor = '#4CAF50';
            
            const x = segment.x * cellSize + 2;
            const y = segment.y * cellSize + 2;
            const size = cellSize - 4;
            
            ctx.fillRect(x, y, size, size);
        });
        
        ctx.shadowBlur = 0;
    }
    
    function render() {
        ctx.fillStyle = '#f0f0f0';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        drawGrid();
        drawFood();
        drawSnake();
    }
    
    function gameLoop() {
        update();
        render();
    }
    
    function init() {
        render();
        gameInterval = setInterval(gameLoop, 150);
    }
    
    function handleResize() {
        const wrapper = canvas.parentElement;
        const maxWidth = Math.min(600, wrapper.clientWidth - 32);
        
        if (window.innerWidth <= 480) {
            canvas.style.width = Math.min(350, maxWidth) + 'px';
            canvas.style.height = Math.min(350, maxWidth) + 'px';
        } else if (window.innerWidth <= 768) {
            canvas.style.width = Math.min(500, maxWidth) + 'px';
            canvas.style.height = Math.min(500, maxWidth) + 'px';
        } else {
            canvas.style.width = '600px';
            canvas.style.height = '600px';
        }
    }
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    window.SnakeGame = {
        reset: resetGame,
        pause: () => clearInterval(gameInterval),
        resume: () => gameInterval = setInterval(gameLoop, 150)
    };
})();
