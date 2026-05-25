// Card Engine — deck, hands, rendering
const SUITS = ['s','h','d','c'];
const SUIT_SYMBOLS = { s: '♠', h: '♥', d: '♦', c: '♣' };
const SUIT_COLORS = { s: 'black', h: 'red', d: 'red', c: 'black' };
const RANKS = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
const RANK_VALUES = { A:14, K:13, Q:12, J:11, T:10, '9':9, '8':8, '7':7, '6':6, '5':5, '4':4, '3':3, '2':2 };
const POSITIONS = ['UTG','MP','CO','BTN','SB','BB'];

function freshDeck() {
  const deck = [];
  for (const suit of SUITS)
    for (const rank of RANKS)
      deck.push({ rank, suit });
  return deck;
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function cardKey(c) { return c.rank + c.suit; }

function cardHTML(c, cls = '') {
  const color = SUIT_COLORS[c.suit];
  return `<span class="card ${cls} ${color}"><span class="card-inner"><span class="rank">${c.rank}</span><span class="suit">${SUIT_SYMBOLS[c.suit]}</span></span></span>`;
}

function handHTML(hand, cls = '') {
  return hand.map(c => cardHTML(c, cls)).join('');
}

function handStr(hand) {
  const sorted = [...hand].sort((a,b) => RANK_VALUES[b.rank] - RANK_VALUES[a.rank]);
  const r1 = sorted[0].rank, r2 = sorted[1].rank;
  const suited = sorted[0].suit === sorted[1].suit;
  if (r1 === r2) return r1 + r2;
  return r1 + r2 + (suited ? 's' : 'o');
}

function dealHand(deck) { return [deck.pop(), deck.pop()]; }

function isPocketPair(hand) { return hand[0].rank === hand[1].rank; }

// Hand strength evaluation for postflop (simplified relative ranking)
function handStrength(hand, board) {
  const all = [...hand, ...board];
  const ranks = all.map(c => RANK_VALUES[c.rank]).sort((a,b) => b-a);
  const suits = all.map(c => c.suit);
  
  const paired = isPocketPair(hand);
  const topPair = board.some(c => c.rank === hand[0].rank) || board.some(c => c.rank === hand[1].rank);
  const overpair = paired && RANK_VALUES[hand[0].rank] > Math.max(...board.map(c => RANK_VALUES[c.rank]));
  const secondPair = !topPair && (hand[0].rank === board[1]?.rank || hand[1].rank === board[1]?.rank);
  const flushDraw = suits.filter(s => s === hand[0].suit).length >= 2 && 
    suits.filter(s => s === hand[0].suit).length + (board.filter(c => c.suit === hand[0].suit).length) >= 4;
  const straightDraw = hasStraightDraw(ranks);
  const twoOver = hand.every(c => RANK_VALUES[c.rank] > Math.max(...board.map(c => RANK_VALUES[c.rank])));
  const air = !topPair && !secondPair && !overpair && !flushDraw && !straightDraw && !twoOver && !paired && RANK_VALUES[hand[0].rank] < 10 && RANK_VALUES[hand[1].rank] < 10;
  
  if (overpair) return 'overpair';
  if (topPair) return 'topPair';
  if (secondPair) return 'secondPair';
  if (paired && RANK_VALUES[hand[0].rank] < Math.min(...board.map(c => RANK_VALUES[c.rank]))) return 'underpair';
  if (flushDraw && (RANK_VALUES[hand[0].rank] >= 10 || RANK_VALUES[hand[1].rank] >= 10)) return 'nutFlushDraw';
  if (flushDraw) return 'flushDraw';
  if (straightDraw && !air) return 'straightDraw';
  if (twoOver) return 'twoOver';
  if (air) return 'air';
  return 'medium';
}

function hasStraightDraw(ranks) {
  const uniq = [...new Set(ranks)].sort((a,b) => b-a);
  let cons = 0, maxCons = 0;
  for (let i = 0; i < uniq.length - 1; i++) {
    if (uniq[i] - uniq[i+1] === 1) { cons++; maxCons = Math.max(maxCons, cons); }
    else { cons = 0; }
  }
  return maxCons >= 2; // 3 connected = open-ended draw
}

// Board texture
function boardTexture(board) {
  if (board.length < 3) return 'preflop';
  const ranks = board.map(c => RANK_VALUES[c.rank]);
  const suits = board.map(c => c.suit);
  const paired = ranks.some((r,i) => ranks.indexOf(r) !== i);
  const monotone = new Set(suits).size === 1;
  const twoTone = new Set(suits).size === 2;
  const highCards = ranks.filter(r => r >= 10).length;
  const connected = hasStraightDraw(ranks);
  
  if (monotone && connected) return 'wet';
  if (monotone) return 'monotone';
  if (paired && highCards >= 2) return 'dynamic';
  if (paired) return 'paired';
  if (highCards >= 2 && connected) return 'wet';
  if (highCards >= 2) return 'high';
  if (connected) return 'connected';
  return 'dry';
}
