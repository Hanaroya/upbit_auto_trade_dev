document.addEventListener('DOMContentLoaded', function () {
  const buttons = document.querySelectorAll('.graph-btn');
  buttons.forEach(button => {
    button.addEventListener('click', function () {
      const coinCode = this.getAttribute('data-coin');
      toggleGraphDisplay(coinCode);
    });
  });
});

let allMainGraphData = [];
let allRSIData = [];
let allStochRSIData = [];
let allMACDData = [];
let mainChart, rsiChart, stochRsiChart, macdChart;

async function toggleGraphDisplay(coinCode) {
  const graphContainer = document.getElementById('graph-container');

  if (graphContainer.style.display === 'block') {
    graphContainer.style.display = 'none';  // 그래프를 숨깁니다.
    return;
  }

  try {
    const response = await fetch(`/coin_graph?coin_code=${coinCode}`);
    const data = await response.json();

    allMainGraphData = data.main_data;
    allRSIData = data.rsi_data;
    allStochRSIData = data.stoch_rsi_data;
    allMACDData = data.macd_data;

    drawMainGraph(allMainGraphData);
    drawRSIGraph(allRSIData);
    drawStochRSIGraph(allStochRSIData);
    drawMACDGraph(allMACDData);

    graphContainer.style.display = 'block';
    window.scrollTo({ top: graphContainer.offsetTop, behavior: 'smooth' });

  } catch (error) {
    console.error('Error fetching graph data:', error);
  }
}

function drawMainGraph(data) {
  const options = {
    series: [{
      name: 'Candles',
      data: data.map(item => ({
        x: new Date(item.date),
        y: [item.open, item.high, item.low, item.close]
      }))
    }, {
      name: 'Volume',
      data: data.map(item => ({
        x: new Date(item.date),
        y: item.volume
      }))
    }],
    chart: {
      type: 'candlestick',
      height: 350,
      width: '100%',
      zoom: {
        enabled: true,
        type: 'x',
        autoScaleYaxis: true
      },
      pan: {
        enabled: true,
        mode: 'x',
        threshold: 10
      },
      animations: {
        enabled: false
      },
      toolbar: {
        tools: {
          pan: true,
          reset: true
        }
      },
      selection: {
        enabled: true,
        type: 'x'
      },
      events: {
        selection: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        },
        zoomed: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        }
      }
    },
    xaxis: {
      type: 'datetime',
      labels: {
        datetimeUTC: false
      },
      min: new Date(data[data.length - 30].date).getTime(),
      max: new Date(data[data.length - 1].date).getTime()
    },
    yaxis: [{
      title: {
        text: 'Price'
      }
    }, {
      opposite: true,
      title: {
        text: 'Volume'
      }
    }],
    tooltip: {
      shared: true,
      intersect: false,
      y: {
        formatter: function (val) {
          return val.toFixed(2);
        }
      }
    },
    markers: {
      size: 0
    },
    stroke: {
      width: [2, 4]
    }
  };

  if (mainChart) {
    mainChart.destroy();
  }

  mainChart = new ApexCharts(document.querySelector("#main-graph"), options);
  mainChart.render();
}

function drawRSIGraph(data) {
  const options = {
    series: [{
      name: 'RSI',
      data: data.map(item => ({
        x: new Date(item.date),
        y: item.rsi
      }))
    }],
    chart: {
      type: 'line',
      height: 225,
      width: '100%',
      zoom: {
        enabled: true,
        type: 'x',
        autoScaleYaxis: true
      },
      pan: {
        enabled: true,
        mode: 'x',
        threshold: 10
      },
      animations: {
        enabled: false
      },
      toolbar: {
        tools: {
          pan: true,
          reset: true
        }
      },
      selection: {
        enabled: true,
        type: 'x'
      },
      events: {
        selection: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        },
        zoomed: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        }
      }
    },
    xaxis: {
      type: 'datetime',
      labels: {
        datetimeUTC: false
      },
      min: new Date(data[data.length - 30].date).getTime(),
      max: new Date(data[data.length - 1].date).getTime()
    },
    stroke: {
      width: 1
    }
  };

  if (rsiChart) {
    rsiChart.destroy();
  }

  rsiChart = new ApexCharts(document.querySelector("#rsi-graph"), options);
  rsiChart.render();
}

function drawStochRSIGraph(data) {
  const options = {
    series: [{
      name: 'Stoch RSI K',
      data: data.map(item => ({
        x: new Date(item.date),
        y: item.rsi_K
      }))
    }, {
      name: 'Stoch RSI D',
      data: data.map(item => ({
        x: new Date(item.date),
        y: item.rsi_D
      }))
    }],
    chart: {
      type: 'line',
      height: 225,
      width: '100%',
      zoom: {
        enabled: true,
        type: 'x',
        autoScaleYaxis: true
      },
      pan: {
        enabled: true,
        mode: 'x',
        threshold: 10
      },
      animations: {
        enabled: false
      },
      toolbar: {
        tools: {
          pan: true,
          reset: true
        }
      },
      selection: {
        enabled: true,
        type: 'x'
      },
      events: {
        selection: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        },
        zoomed: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        }
      }
    },
    xaxis: {
      type: 'datetime',
      labels: {
        datetimeUTC: false
      },
      min: new Date(data[data.length - 30].date).getTime(),
      max: new Date(data[data.length - 1].date).getTime()
    },
    stroke: {
      width: 1
    }
  };

  if (stochRsiChart) {
    stochRsiChart.destroy();
  }

  stochRsiChart = new ApexCharts(document.querySelector("#stoch-rsi-graph"), options);
  stochRsiChart.render();
}

function drawMACDGraph(data) {
  const options = {
    series: [{
      name: 'MACD',
      data: data.map(item => ({
        x: new Date(item.date),
        y: item.macd
      }))
    }, {
      name: 'Signal',
      data: data.map(item => ({
        x: new Date(item.date),
        y: item.signal
      }))
    }],
    chart: {
      type: 'line',
      height: 225,
      width: '100%',
      zoom: {
        enabled: true,
        type: 'x',
        autoScaleYaxis: true
      },
      pan: {
        enabled: true,
        mode: 'x',
        threshold: 10
      },
      animations: {
        enabled: false
      },
      toolbar: {
        tools: {
          pan: true,
          reset: true
        }
      },
      selection: {
        enabled: true,
        type: 'x'
      },
      events: {
        selection: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        },
        zoomed: function (chartContext, { xaxis }) {
          chartContext.updateOptions({
            xaxis: {
              min: xaxis.min,
              max: xaxis.max
            }
          });
        }
      }
    },
    xaxis: {
      type: 'datetime',
      labels: {
        datetimeUTC: false
      },
      min: new Date(data[data.length - 30].date).getTime(),
      max: new Date(data[data.length - 1].date).getTime()
    },
    stroke: {
      width: 1
    }
  };

  if (macdChart) {
    macdChart.destroy();
  }

  macdChart = new ApexCharts(document.querySelector("#macd-graph"), options);
  macdChart.render();
}

function toggleMenu() {
    document.getElementById("myDropdown").classList.toggle("show");
  }

  function goToHome() {
    window.location.href = "/";
  }

  function logout() {
    window.location.href = `/logout`;
  }

  window.onclick = function(e) {
    if (!e.target.matches('.dropbtn')) {
      var myDropdown = document.getElementById("myDropdown");
      if (myDropdown.classList.contains('show')) {
        myDropdown.classList.remove('show');
      }
    }
  }

  function openPopup(type, coinId) {
    const popup = document.getElementById('popup');
    const popupContent = document.getElementById('popup-content');
    popup.style.display = 'block';

    if (type === 'buy') {
      fetch(`/get_real_balance`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
          const balance = data.volume;

          popupContent.innerHTML = `
            <h3>코인 구매</h3>
            <p>사용 가능 금액: $${balance}</p>
            <input id="buy-amount" type="number" placeholder="금액 입력"><br>
            <input id="buy-price" type="number" placeholder="희망 가격 입력"><br>
            <button onclick="buyUrgent(${balance}, '${coinId}')">시장가 구매</button>
            <button onclick="buyLimit('${coinId}')">지정가 구매</button>
            <button onclick="cancelBuyOrder('${coinId}')">구매 주문 취소</button>
          `;
        })
        .catch(error => console.error('잔액 조회 오류:', error));
    } else if (type === 'sell') {
      fetch(`/get_real_volume?coin_id=${coinId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ coin_id: coinId })
      })
        .then(response => response.json())
        .then(data => {
          const totalVolume = data.volume;

          popupContent.innerHTML = `
            <h3>코인 판매</h3>
            <p>사용 가능 수량: ${totalVolume}</p>
            <input id="sell-volume" type="range" min="0" max="100" value="0">
            <span id="sell-percentage">0%</span><br>
            <input id="sell-price" type="number" placeholder="희망 가격 입력"><br>
            <button onclick="sellUrgent(${totalVolume}, '${coinId}')">시장가 판매</button>
            <button onclick="sellLimit(${totalVolume}, '${coinId}')">지정가 판매</button>
            <button onclick="cancelSellOrder('${coinId}')">판매 주문 취소</button><br>
            <button onclick="endSimulation('${coinId}')">시뮬레이션 종료</button>
          `;

          const sellSlider = document.getElementById('sell-volume');
          sellSlider.oninput = function() {
            document.getElementById('sell-percentage').innerText = this.value + '%';
          };
        })
        .catch(error => console.error('수량 조회 오류:', error));
    }
  }

  function closePopup() {
    document.getElementById('popup').style.display = 'none';
  }

  async function buyUrgent(balance, coinId) {
    const amount = parseFloat(document.getElementById('buy-amount').value);
    const realBalance = parseFloat(balance);

    if (amount > realBalance) {
      showAlert("구매 가능 금액을 초과 했습니다.");
      return;
    }

    const response = await fetch(`/buy_urgent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("시뮬레이션 중에는 실거래가 불가능합니다");
    }
    closePopup();
  }

  async function buyLimit(coinId) {
    const amount = parseFloat(document.getElementById('buy-amount').value);
    const price = parseFloat(document.getElementById('buy-price').value);

    const response = await fetch(`/buy_limit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, price, coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("시뮬레이션 중에는 실거래가 불가능합니다");
    }
    closePopup();
  }

  async function sellUrgent(totalVol, coinId) {
    const percentage = parseFloat(document.getElementById('sell-volume').value);
    const totalVolume = parseFloat(totalVol);
    const volume = totalVolume * (percentage / 100);

    if (percentage === 0) {
      showAlert("볼륨값이 0일때 거래 불가능합니다.");
      return;
    }

    const response = await fetch(`/sell_urgent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ volume, coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("실물 거래가 불가능합니다");
    }
    closePopup();
  }

  async function sellLimit(totalVol, coinId) {
    const percentage = parseFloat(document.getElementById('sell-volume').value);
    const totalVolume = parseFloat(totalVol);
    const volume = totalVolume * (percentage / 100);
    const price = parseFloat(document.getElementById('sell-price').value);

    if (percentage === 0) {
      showAlert("볼륨값이 0일때 거래 불가능합니다.");
      return;
    }

    const response = await fetch(`/sell_limit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ volume, price, coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("실물 거래가 불가능합니다");
    }
    closePopup();
  }

  async function endSimulation(coinId) {
    const response = await fetch(`/simulation_sell?coin_id=${coinId}`, {
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("실제 거래중인 코인은 코인 목록에서 삭제 불가능합니다");
    }
    closePopup();
  }

  function showAlert(message) {
    const alertPopup = document.getElementById('alert-popup');
    const alertMessage = document.getElementById('alert-message');
    alertMessage.innerText = message;
    alertPopup.style.display = 'block';
    setTimeout(() => {
      alertPopup.style.display = 'none';
    }, 5000);
  }

  // 슬라이드 기능을 위한 코드 추가
  document.addEventListener('DOMContentLoaded', function() {
    const tableContainer = document.querySelector('.table-container');
    let isDown = false;
    let startX;
    let scrollLeft;

    tableContainer.addEventListener('mousedown', (e) => {
      isDown = true;
      tableContainer.classList.add('active');
      startX = e.pageX - tableContainer.offsetLeft;
      scrollLeft = tableContainer.scrollLeft;
    });

    tableContainer.addEventListener('mouseleave', () => {
      isDown = false;
      tableContainer.classList.remove('active');
    });

    tableContainer.addEventListener('mouseup', () => {
      isDown = false;
      tableContainer.classList.remove('active');
    });

    tableContainer.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - tableContainer.offsetLeft;
      const walk = (x - startX) * 3; // 스크롤 속도 조정
      tableContainer.scrollLeft = scrollLeft - walk;
    });
  });

  async function cancelBuyOrder(coinId) {
    const response = await fetch(`/cancel_buy_order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("구매 주문 취소에 실패했습니다.");
    } else {
      showAlert("구매 주문이 취소되었습니다.");
    }
    closePopup();
  }

  async function cancelSellOrder(coinId) {
    const response = await fetch(`/cancel_sell_order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coin_id: coinId })
    });
    const result = await response.json();
    if (result.result === -1) {
      showAlert("판매 주문 취소에 실패했습니다.");
    } else {
      showAlert("판매 주문이 취소되었습니다.");
    }
    closePopup();
  }