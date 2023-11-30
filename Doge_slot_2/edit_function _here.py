    function createCashOutButton() {
        const cashOutButton = document.createElement('button');
        cashOutButton.textContent = 'cashOut';
        cashOutButton.style.width = '160px';
        cashOutButton.style.height = '55px';
        cashOutButton.style.position = 'absolute';
        cashOutButton.style.left = '840px';
        cashOutButton.style.top = '15px';
        cashOutButton.style.backgroundColor = 'transparent';
        cashOutButton.style.color = 'transparent';
        cashOutButton.style.fontSize = '20px';
        cashOutButton.style.border = 'none';
        cashOutButton.style.borderRadius = '5px';
        cashOutButton.style.zIndex = 4;

        cashOutButton.style.cursor = 'pointer';
        container.appendChild(cashOutButton);
