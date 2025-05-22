// 获取并渲染市场指数（多个市场）
fetch('/api/all_indices')
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('market-index');
    container.innerHTML = '';

    for (const group of data.groups) {
      const row = document.createElement('div');
      row.className = 'index-row';

      group.indices.forEach(index => {
        const isUp = index.change >= 0;
        const box = document.createElement('div');
        box.className = 'index-box';
        box.innerHTML = `
          ${index.name}:
          <span class="${isUp ? 'up' : 'down'}">
            ${index.price.toFixed(2)} (${isUp ? '+' : ''}${index.change.toFixed(2)}%)
          </span>
        `;
        row.appendChild(box);
      });

      container.appendChild(document.createElement('h3')).textContent = group.market;
      container.appendChild(row);
    }

    document.getElementById('data-date').textContent = `数据更新日期：${data.date}`;
  })
  .catch(() => {
    document.getElementById('market-index').innerHTML = '<div class="index-box">加载失败</div>';
  });
