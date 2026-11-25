"use strict";
const MASTER="EQDbKihXMZuNfl7m7VcNrHIyYYYgCFPhccIqNN_ocNn-PBCb";
const texts = {
  "ru": {
    "navLiquidity":"🔁 Торговые пулы","navSupply":"❄️ Заморозка и 🔒 стейкинг","filterButton":"Фильтр", "filterByBadges":"Метки кошельков", "filterReset":"Сбросить",
    "filterHint":"При выборе нескольких меток показываются кошельки, имеющие все выбранные метки.",
    "filterSearchPlaceholder":"Найти метку…",
    "volumeTitle": "Объём сделок",
    "volumeEmpty": "За этот период сделки не найдены",
    "largeTrades": "Крупные сделки",
    "minimumSize": "От, GRAM",
    "walletSearch": "Поиск кошелька",
    "walletPlaceholder": "Адрес кошелька или .ton-домен",
    "walletFind": "Найти",
    "walletPending": "Проверяем кошелёк…",
    "walletInvalid": "Введите корректный адрес TON или .ton-домен.",
    "walletDomainMissing": "Домен не привязан к кошельку или не найден.",
    "walletNetwork": "Сервис TON недоступен. Попробуйте ещё раз.",
    "walletBalance": "Баланс",
    "walletBalanceUnknown": "Данные о балансе недоступны",
    "walletTop": "Место в топ‑20 держателей",
    "walletOperations": "Последние операции по токену",
    "walletNoOperations": "В загруженной истории операций нет.",
    "rankGained": "Подъём на",
    "rankLost": "Снижение на",
    "badgeLegend": "О метках",
    "noLargeTrades": "Сделок по этим условиям нет.",
    "badgeStaking": "От 500 000 LUDOMAN в JVault, включая заявки на вывод.",
    "badgeAuthor": "Любая NFT из авторской коллекции.",
    "badgeVnuk": "Более 200 000 VNUK или NFT из коллекции VNUK.",
    "badgeJoystick": "От 200 000 JSI или NFT из коллекции Joystick.",
    "badgePhoenix": "От 200 000 PHX.",
    "badgeBlue": "NFT из коллекции, указанной в ссылке на метке.",
    "badgeFragment": "Владелец NFT анонимного номера Fragment",
    "badgeOg": "Более пяти лет с первой активации кошелька.",
    "badgeBurn": "Сожжено от 1 000 токенов проекта, включая переводы на нулевой адрес.",
    "badgeArni": "Более 50 000 ARNI.",
    "badgeNapiwas": "От 1 000 000 NAPIWAS.",
    "badgeDnsLinked": "Привязан в TON DNS",
    "badgeDigits": "Четырёхзначный .ton-домен в кошельке или подтверждённая привязка в TON DNS.",
    "badgeSub": "Владение субдоменом .socool.ton.",
    "blueCollection":"Открыть NFT-коллекцию","activated":"Активация","burnBadge":"Сожжено от 1 000 токенов","toZero":"На нулевой адрес","operationDetails":"Подробности операции","supplyTitle":"❄️ Заморозка и 🔒 стейкинг","supplyFrozen":"❄️ Заморожено","supplyFrozenHint":"Остатки в контрактах TonRaffles","supplyStaked":"🔒 Стейкинг","supplyStakedHint":"Позиции JVault, включая заявки на вывод","supplyUsdHint":"Оценка по последней доступной сделке и GRAM/USD",
    "intro": "Сделки, держатели и сжигания $LUDOMAN в сети TON.",
    "swap": "Обмен на STON.fi",
    "price": "📈 Капитализация LUDOMAN",
    "summary": "📊 LUDOMAN за 24 часа",
    "activity": "🔄 Операции",
    "wallets": "🏆 Рейтинги",
    "buy": "Покупка",
    "sell": "Продажа",
    "burn": "Сжигание",
    "holders": "Держатели",
    "sellers": "Продавцы",
    "services": "⚙️ Сервисы",
    "more": "Показать ещё",
    "less": "Свернуть",
    "copy": "Копировать адрес",
    "copied": "Скопировано",
    "no": "Нет данных",
    "noTrades": "За этот период в проверенной истории нет сделок.",
    "partial": "Частичная история",
    "since": "История с",
    "updated": "Данные на",
    "none": "За период записей нет",
    "sold": "Продано LUDOMAN",
    "balance": "Баланс LUDOMAN",
    "all": "Показать все",
    "delayed": "Обновление задерживается",
    "chart": "Оценка капитализации",
    "burnCount": "Сжигания",
    "projectDirectory": "Сайт Ludoman",
    "navMarket": "📈 Рынок",
    "links": "🔗 Полезные ссылки",
    "exploreContract": "Контракт",
    "toMarket": "Открыть рынок",
    "up": "Наверх ↑",
    "capMethod": "Цена сделки на STON.fi × текущее общее предложение LUDOMAN, включая заблокированные токены. USD — по историческому курсу GRAM/USD от CoinGecko.",
    "capPartial": "Изменение по доступной истории",
    "capNoTrades": "Новых сделок за период нет · последний известный уровень",
    "capLow": "Минимум", "capHigh": "Максимум",
    "burnKey": "🔥 Сжигание",
    "pointHint": "Коснись графика или выбери точку стрелками ← →.",
    "activityHint": "Прямые сделки LUDOMAN / GRAM на STON.fi и DeDust и подтверждённые сжигания.",
    "filterAll": "Все",
    "buys": "Покупки",
    "sells": "Продажи",
    "people": "Кошельки",
    "buyers": "покупатели",
    "sellersLabel": "продавцы",
    "volumeUnit": "Объём",
    "burnedTotal": "Сожжено",
    "events": "Операций",
    "openTx": "На gram.org",
    "allHolders": "Всего адресов",
    "holderHint": "Крупнейшие остатки LUDOMAN и доля от общего предложения.",
    "sellerHint": "Кошельки по сумме проданных LUDOMAN за выбранный период.",
    "projectResources": "Сообщество и рынок",
    "contractLabel": "Контракт LUDOMAN",
    "feedTime": "Сделки",
    "periodNames": [
      "1 час",
      "24 часа",
      "Неделя",
      "Месяц",
      "6 мес.",
      "Год"
    ],
    "dayLabels": [
      "24 часа",
      "7 дней",
      "30 дней"
    ],
    "withBadges": "Только адреса с доменной меткой",
    "noneTagged": "Среди проверенных адресов для этого фильтра записей нет."
  },
  "en": {
    "navLiquidity":"🔁 Trading pools","navSupply":"❄️ Locks and 🔒 staking","filterButton":"Filter", "filterByBadges":"Wallet badges", "filterReset":"Reset",
    "filterHint":"Selecting multiple badges shows wallets that have all selected badges.",
    "filterSearchPlaceholder":"Search badges…",
    "volumeTitle": "Trade volume",
    "volumeEmpty": "No trades found for this period",
    "largeTrades": "Large trades",
    "minimumSize": "Minimum GRAM",
    "walletSearch": "Wallet search",
    "walletPlaceholder": "TON address or .ton domain",
    "walletFind": "Find",
    "walletPending": "Checking wallet…",
    "walletInvalid": "Enter a valid TON address or .ton domain.",
    "walletDomainMissing": "The domain was not found or has no wallet linked.",
    "walletNetwork": "TON data is unavailable. Try again.",
    "walletBalance": "Balance",
    "walletBalanceUnknown": "Balance data is unavailable",
    "walletTop": "Top 20 holder rank",
    "walletOperations": "Recent token activity",
    "walletNoOperations": "No activity in the loaded history.",
    "rankGained": "Places gained:",
    "rankLost": "Places lost:",
    "badgeLegend": "Badge guide",
    "noLargeTrades": "No trades match these filters.",
    "badgeStaking": "At least 500,000 LUDOMAN in JVault, including pending withdrawals.",
    "badgeAuthor": "An NFT from the author collection.",
    "badgeVnuk": "Over 200,000 VNUK or an NFT from the VNUK collection.",
    "badgeJoystick": "At least 200,000 JSI or an NFT from the Joystick collection.",
    "badgePhoenix": "At least 200,000 PHX.",
    "badgeBlue": "An NFT from the collection linked on the badge.",
    "badgeFragment": "Owns a Fragment anonymous number NFT",
    "badgeOg": "Over five years since the wallet was first activated.",
    "badgeBurn": "At least 1,000 project tokens burned, including transfers to the zero address.",
    "badgeArni": "Over 50,000 ARNI.",
    "badgeNapiwas": "At least 1,000,000 NAPIWAS.",
    "badgeDnsLinked": "Linked in TON DNS",
    "badgeDigits": "A four-digit .ton domain owned by the wallet or verified as linked in TON DNS.",
    "badgeSub": "Ownership of a .socool.ton subdomain.",
    "blueCollection":"Open NFT collection","activated":"Activated","burnBadge":"Burned at least 1,000 tokens","toZero":"Transfer to zero address","operationDetails":"Transaction details","supplyTitle":"❄️ Frozen and 🔒 staking","supplyFrozen":"❄️ Frozen","supplyFrozenHint":"Balances in TonRaffles contracts","supplyStaked":"🔒 Staking","supplyStakedHint":"JVault positions, including pending withdrawals","supplyUsdHint":"Estimate from latest available trade and GRAM/USD",
    "intro": "Trades, holders and $LUDOMAN burns on TON.",
    "swap": "Swap on STON.fi",
    "price": "📈 LUDOMAN market cap",
    "summary": "📊 LUDOMAN in 24 hours",
    "activity": "🔄 Activity",
    "wallets": "🏆 Rankings",
    "buy": "Buy",
    "sell": "Sell",
    "burn": "Burn",
    "holders": "Holders",
    "sellers": "Sellers",
    "services": "⚙️ Services",
    "more": "Show more",
    "less": "Collapse",
    "copy": "Copy address",
    "copied": "Copied",
    "no": "No data",
    "noTrades": "No trades in the verified history for this period.",
    "partial": "Partial history",
    "since": "History from",
    "updated": "Data as of",
    "none": "No records for this period",
    "sold": "LUDOMAN sold",
    "balance": "LUDOMAN balance",
    "all": "Show all",
    "delayed": "Update overdue",
    "chart": "Estimated market cap",
    "burnCount": "Burns",
    "projectDirectory": "Ludoman website",
    "navMarket": "📈 Market",
    "links": "🔗 Useful links",
    "exploreContract": "Contract",
    "toMarket": "Open market",
    "up": "Back to top ↑",
    "capMethod": "STON.fi trade price × current total LUDOMAN supply, including locked tokens. USD uses historical GRAM/USD rates from CoinGecko.",
    "capPartial": "Change over available history",
    "capNoTrades": "No new trades in this period · last known level",
    "capLow": "Low", "capHigh": "High",
    "burnKey": "🔥 Burn",
    "pointHint": "Tap the chart or use the ← → arrow keys to inspect a trade.",
    "activityHint": "Direct LUDOMAN / GRAM swaps on STON.fi and DeDust, plus confirmed burns.",
    "filterAll": "All",
    "buys": "Buys",
    "sells": "Sells",
    "people": "Wallets",
    "buyers": "buyers",
    "sellersLabel": "sellers",
    "volumeUnit": "Volume",
    "burnedTotal": "Burned",
    "events": "Transactions",
    "openTx": "View on gram.org",
    "allHolders": "Total addresses",
    "holderHint": "Largest LUDOMAN balances and their share of the total supply.",
    "sellerHint": "Wallets ranked by total LUDOMAN sold during the selected period.",
    "projectResources": "Community and market",
    "contractLabel": "LUDOMAN contract",
    "feedTime": "Trades",
    "periodNames": [
      "1 hour",
      "24 hours",
      "Week",
      "Month",
      "6 mo.",
      "Year"
    ],
    "dayLabels": [
      "24 hours",
      "7 days",
      "30 days"
    ],
    "withBadges": "Only wallets with a domain badge",
    "noneTagged": "No records from verified domain holders match this filter."
  }
};
let feedKind="all";
const $=id=>document.getElementById(id);
let snapshot=JSON.parse($("snapshot").textContent), lang="ru", period=1, ranking="holders", sellerDays=1, expanded=false, currency="GRAM";
let syncState={phase:"idle",checkedAt:0};
try{lang=localStorage.getItem("ludoman-lang")==="en"?"en":"ru";currency=localStorage.getItem("ludoman-currency")==="USD"?"USD":"GRAM"}catch{}
const t=key=>texts[lang][key], day=86400, ranges=[3600,day,7*day,30*day,182*day,365*day];
function el(tag,txt,cls){const e=document.createElement(tag);if(txt!==undefined)e.textContent=txt;if(cls)e.className=cls;return e}
function link(href,txt){const a=el("a",txt);a.href=href;a.target="_blank";a.rel="noopener noreferrer";return a}
function format(n,d=1){
 const number=Number(n);
 if(!Number.isFinite(number))return "—";
 if(number!==0&&Math.abs(number)<0.05)return (number<0?"−":"")+"<"+(lang==="ru"?"0,1":"0.1");
 return number.toLocaleString(lang,{minimumFractionDigits:1,maximumFractionDigits:1});
}
function stamp(s){return s?new Date(s*1000).toLocaleString(lang,{month:"short",day:"numeric",hour:"2-digit",minute:"2-digit",year:"numeric"}):"—"}
function short(w){return w?w.slice(0,6)+"…"+w.slice(-5):"—"}
// Use a user-friendly TON address for explorer links and the visible short label.
function explorerAddress(raw,bounceable=false) {
  if (!/^(-1|0):[0-9a-f]{64}$/i.test(raw)) return raw;
  const [chain, hex] = raw.split(":");
  const bytes = [bounceable?0x11:0x51, Number(chain) & 255, ...hex.match(/../g).map(byte => parseInt(byte,16))];
  let crc = 0;
  for (const byte of bytes) {
    crc ^= byte << 8;
    for (let bit=0; bit<8; bit++) crc = ((crc << 1) ^ ((crc & 0x8000) ? 0x1021 : 0)) & 65535;
  }
  return btoa(String.fromCharCode(...bytes, crc >> 8, crc & 255)).replaceAll("+","-").replaceAll("/","_");
}
function addr(raw,name) {
  const wallet=explorerAddress(raw);
  const a=link("https://gram.org/address/"+encodeURIComponent(wallet),name||short(wallet));
  a.title=wallet+" · gram.org";
  return a;
}
const walletLabels = {
  ru:{buy:"Покупатель",sell:"Продавец",burn:"Сжигание",activeBuy:"Посл. покупка",activeSell:"Посл. продажа",
      digits:"4 цифры",checked:"Проверено владение",moreNames:"Ещё домены",
      key:"Цвет адреса показывает роль кошелька в этой операции.", holderKey:"Цвет адреса — по последней сделке в отслеживаемых пулах. Серый — сделка не найдена."},
  en:{buy:"Buyer",sell:"Seller",burn:"Burn",activeBuy:"Last trade: buy",activeSell:"Last trade: sell",
      digits:"4 digits",checked:"Ownership checked",moreNames:"More domains",
      key:"The address colour identifies the wallet’s role in this transaction.",holderKey:"Address colours show the last observed trade across tracked pools. Grey means no trade was found in the archive."}
};
const wl=key=>walletLabels[lang][key];
function freshIdentity(wallet){
  const record=snapshot.identity?.byWallet?.[wallet];
  return record?.checked>=Date.now()/1000-day ? record : null;
}
function linkedDomain(wallet){
  return freshIdentity(wallet)?.domain||null;
}
const fourDigitDomain=/^[0-9]{4}\.ton$/;
function numericDomains(wallet,verifiedDomain){
  const record=freshIdentity(wallet);
  const holders=snapshot.holders;
  const holderName=holders?.asOf>=Date.now()/1000-day
    ? holders.holders.find(row=>row.wallet===wallet)?.name : null;
  const linked=[record?.domain,...(record?.linkedDigits||[]),holderName,verifiedDomain]
    .filter(name=>fourDigitDomain.test(name||""));
  const owned=(snapshot.domains?.byWallet?.[wallet]?.digits||[]).filter(name=>fourDigitDomain.test(name));
  return {names:[...new Set([...linked,...owned])],linked:new Set(linked)};
}
function hasDomainBadge(wallet){
  return Boolean(linkedDomain(wallet)||numericDomains(wallet).names.length);
}

const fragmentCollection="0:0e41dc1dc3c9067ed24248580e12b3359818d83dee0304fabcf80845eafafdb2";
const authorCollection="EQAhaFPX9zIBVYe_vfy3dudCkxJDjSoMjj59KndtHKcqo3iy";
const projectBadgeDefs=[
  ["author","author NFT",""],
  ["staking","","https://jvault.xyz/staking/v2/stake/LUDOMAN"],
  ["vnuk","VNUK","https://t.me/mRvnukICHlife"],
  ["joystick","Joystick","https://t.me/joystickpro"],
  ["phoenix","Phoenix","https://t.me/PHXPW"],
  ["arni","ARNI","https://t.me/TonArnold"],
  ["napiwas","NAPIWAS","https://t.me/NAPIWASofficial"],
  ["blueNft","","https://getgems.io/collection/EQBmoucipH0QT_qpd361W-9zUlyFsSl1FD1GIY0AfXdpPQW8"]
];
function appendProjectBadges(wrapper,wallet,verifiedDomain,ownsFragment){
  const data=snapshot.badges?.sources;
  const identity=snapshot.identity?.byWallet?.[wallet];
  const badges=el("span",undefined,"projectBadges");
  if(identity?.activated){
    const date=new Date(identity.activated*1000);
    const fifth=new Date(date);
    fifth.setUTCFullYear(date.getUTCFullYear()+5);
    if(fifth.getUTCMonth()!==date.getUTCMonth())fifth.setUTCDate(0);
    if(Date.now()>fifth.getTime()){
      const badge=el("span",undefined,"projectBadge og");
      badge.append(el("span","OG"));
      badge.title=t("activated")+" "+stamp(identity.activated);
      badge.setAttribute("aria-label","OG · "+badge.title);
      badges.append(badge);
    }
  }
  const fragment=snapshot.fragmentNumbers?.byWallet?.[wallet];
  if(ownsFragment ?? (fragment?.owns && fragment.checkedAt>=Date.now()/1000-2*day)){
    const badge=el("span","+888","projectBadge fragmentNumber");
    badge.title=t("badgeFragment");
    badge.setAttribute("aria-label","+888 · "+badge.title);
    badges.append(badge);
  }
  const domains=snapshot.domains?.byWallet?.[wallet];
  const digits=numericDomains(wallet,verifiedDomain);
  appendDomainBadge(wrapper,digits.names,"digits",domains?.digitsAt,digits.linked);
  function match(key){
    const source=data?.[key];
    return source?.asOf>=Date.now()/1000-24*3600 && source.wallets?.[wallet];
  }
  for(const [key,label,url] of projectBadgeDefs){
    const value=match(key)||((key==="vnuk"||key==="joystick")&&match(key+"Nft"));
    if(!value)continue;
    const target=key==="author"
      ?"https://getgems.io/collection/"+authorCollection+"/"+explorerAddress(value,true)
      :url;
    const badge=link(target,"");
    badge.className="projectBadge "+key;
    if(key==="napiwas"){
      const icon=el("span",undefined,"beerIcon");
      icon.setAttribute("aria-hidden","true");
      badge.append(icon);
    }else if(key!=="author"){
      const icon=$("badge-icon-"+key).content.firstElementChild.cloneNode();
      badge.append(icon);
    }
    if(label)badge.append(el("span",label,"badgeLabel"));
    if(key==="blueNft"){
      badge.title=t("blueCollection");
      badge.setAttribute("aria-label",badge.title);
    }
    if(key==="staking"){
      badge.title=lang==="ru"?"JVault · от 500 000 LUDOMAN":"JVault · 500,000+ LUDOMAN";
      badge.setAttribute("aria-label",badge.title);
    }
    badges.append(badge);
  }
  if(burnTotals.get(wallet)>=1000n*10n**9n){
    const badge=el("span","🔥","projectBadge burner");
    badge.title=t("burnBadge");
    badge.setAttribute("aria-label",badge.title);
    badges.append(badge);
  }
  if(badges.childElementCount)wrapper.append(badges);
}

function appendDomainBadge(badges,names,type,checked,linked){
  if(!names.length)return;
  const name=names[0];
  const badge=el("span",name,"domainBadge "+type);
  const proof=linked?.has(name)?t("badgeDnsLinked"):wl("checked")+" · "+stamp(checked);
  badge.title=wl(type)+" · "+proof;
  badges.append(badge);
  if(names.length>1){
    const rest=el("details",undefined,"domainDetails");
    rest.append(el("summary",wl("moreNames")+" (+"+(names.length-1)+")"),
      el("span",names.slice(1).join(" · ")));
    badges.append(rest);
  }
}
function walletIdentity(raw,name,kind,{activity=false, holder=false, verifiedDomain, ownsFragment}={}){
  const wrapper=el("span",undefined,"walletIdentity");
  const identity=snapshot.identity?.byWallet?.[raw];
  const domain=linkedDomain(raw);
  const address=addr(raw,(holder&&identity?.role)||domain||name);
  address.className="walletAddress "+(kind||"neutral");
  if(!activity&&holder&&kind){
    wrapper.append(el("span",wl(kind==="buy"?"activeBuy":"activeSell"),"walletRole "+kind));
  }
  wrapper.append(address);
  // Flag only identified service accounts. Unknown wallets are never guessed.
  if(holder&&typeof identity?.role==="string"&&identity.role.trim()){
    wrapper.classList.add("serviceWallet");
    const service=el("span","⚙️","serviceGear");
    service.title=(lang==="ru"?"Сервисный кошелёк · ":"Service wallet · ")+identity.role;
    if(identity.roleSource==="https://github.com/tonkeeper/ton-assets/blob/main/accounts.json"){
      service.title+=(lang==="ru"?" · Метка Tonkeeper; открыть источник":" · Tonkeeper label; open source");
      const proof=el("a");
      proof.href=identity.roleSource;proof.target="_blank";proof.rel="noopener noreferrer";
      proof.setAttribute("aria-label",service.title);
      proof.append(service);wrapper.append(proof);
    }else wrapper.append(service);
    service.setAttribute("aria-label",service.title);
  }
  appendProjectBadges(wrapper,raw,verifiedDomain,ownsFragment);
  return wrapper;
}
function burnRows(){
  const rows=new Map();
  for(const r of [...(snapshot.zeroBurns?.rows||[]),...(snapshot.burns?.rows||[])])rows.set(r.tx,r);
  return [...rows.values()];
}
function tokenUnits(value){
  const [whole,fraction=""]=String(value).split(".");
  if(!/^\d+$/.test(whole)||!/^\d{0,9}$/.test(fraction))return 0n;
  return BigInt(whole)*10n**9n+BigInt(fraction.padEnd(9,"0"));
}
let burnTotals;
function updateBurnTotals(){
  burnTotals=new Map();
  for(const row of burnRows()){
    burnTotals.set(row.wallet,(burnTotals.get(row.wallet)||0n)+tokenUnits(row.ludoman));
  }
}
function lastTradeByWallet(){
  const latest=new Map();
  for(const r of snapshot.trades?.rows||[]){
    if(!latest.has(r.wallet))latest.set(r.wallet,r.kind);
  }
  return latest;
}
function tx(row){const a=link("https://gram.org/tx/"+row.tx,t("openTx"));a.title=row.tx;return a}
function countFormat(number){return Number.isFinite(Number(number))?Math.trunc(Number(number)).toLocaleString(lang):"—"}
function select(id,labels,selected,onClick){const node=$(id);node.replaceChildren();labels.forEach((name,i)=>{const b=el("button",name);b.classList.toggle("on",i===selected);b.setAttribute("aria-pressed",i===selected);b.onclick=()=>onClick(i);node.append(b)})}
function freshness(s){if(!s?.asOf)return t("no");return t("updated")+" "+stamp(s.asOf)+(Date.now()/1000-s.asOf>4*3600?" · "+t("delayed"):"")}
function coverage(section,cut){return section&&section.since>cut?t("partial")+" · "+t("since")+" "+stamp(section.since):""}
function capFormat(n,compact=false){
 const number=Number(n);
 if(!Number.isFinite(number))return "—";
 if(number!==0&&Math.abs(number)<0.05)return (number<0?"−":"")+"<"+(lang==="ru"?"0,1":"0.1");
 return number.toLocaleString(lang,{minimumFractionDigits:1,maximumFractionDigits:1,...(compact?{notation:"compact"}:{})});
}
function svg(tag,attrs){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n}
function volumeBars(start,end,width,left,right){
 const main=$("tradeVolume");
 const rows=snapshot.trades?.rows||[];
 const bins=Array.from({length:30},()=>({buy:0,sell:0}));
 const step=(end-start)/bins.length;
 if(step>0){
   for(const row of rows){
     if((row.kind!=="buy"&&row.kind!=="sell")||row.time<start||row.time>end)continue;
     const value=Number(row.ton);
     if(!Number.isFinite(value)||value<=0)continue;
     bins[Math.min(bins.length-1,Math.floor((row.time-start)/step))][row.kind]+=value;
   }
 }
 const totals=bins.reduce((sum,bin)=>({buy:sum.buy+bin.buy,sell:sum.sell+bin.sell}),{buy:0,sell:0});
 $("volumeBuys").textContent=t("buys")+" · "+format(totals.buy)+" GRAM";
 $("volumeSells").textContent=t("sells")+" · "+format(totals.sell)+" GRAM";
 const peak=Math.max(...bins.map(bin=>bin.buy+bin.sell));
 $("volumeEmpty").hidden=peak>0;
 const plot=svg("svg",{viewBox:"0 0 "+width+" 58",preserveAspectRatio:"none",role:"img","aria-label":t("volumeTitle")});
 const spacing=(right-left)/bins.length;
 if(peak>0){
   plot.append(svg("path",{d:"M"+left+" 56H"+right,stroke:"#344b5b"}));
   for(const [i,bin] of bins.entries()){
     let floor=56;
     const bars=svg("g",{});
     const title=svg("title",{});
     title.textContent=stamp(start+i*step)+" · "+t("buys")+" "+format(bin.buy)+" · "+t("sells")+" "+format(bin.sell)+" GRAM";
     bars.append(title);
     for(const kind of ["buy","sell"]){
       if(!bin[kind])continue;
       const height=bin[kind]/peak*52;
       floor-=height;
       bars.append(svg("rect",{x:left+i*spacing,y:floor,width:Math.max(1,spacing-1),height,fill:kind==="buy"?"#57cba1":"#f27f8a"}));
     }
     if(bars.childElementCount>1)plot.append(bars);
   }
 }
 main.replaceChildren(...(peak>0?[plot]:[]));
}

let lookupResult,lookupPending;
const walletPattern=/^(0|-1):[0-9a-f]{64}$/i;
const dnsPattern=/^(?:[a-z0-9-]+\.)+ton$/i;

function rawLookupAddress(value){
 if(walletPattern.test(value))return value.toLowerCase();
 if(!/^[A-Za-z0-9+/_-]{48}$/.test(value))return null;
 const bytes=atob(value.replaceAll("-","+").replaceAll("_","/"));
 const tag=bytes.charCodeAt(0),chain=bytes.charCodeAt(1);
 if(![0x11,0x51].includes(tag)||![0,255].includes(chain))return null;
 const hex=Array.from(bytes.slice(2,34),c=>c.charCodeAt(0).toString(16).padStart(2,"0")).join("");
 const raw=(chain===255?-1:0)+":"+hex;
 const supplied=value.replaceAll("+","-").replaceAll("/","_");
 return explorerAddress(raw,tag===0x11)===supplied?raw:null;
}

async function lookupData(path,signal){
 const result=await fetch("https://tonapi.io/v2"+path,{signal,headers:{Accept:"application/json"}});
 if(result.status===404)return null;
 if(!result.ok)throw new Error("Wallet lookup failed");
 return result.json();
}

function renderLookup(){
 $("walletQuery").placeholder=t("walletPlaceholder");
 $("walletQuery").setAttribute("aria-label",t("walletPlaceholder"));
 $("walletFind").textContent=t("walletFind");
 const target=$("walletResult");target.replaceChildren();
 if(!lookupResult){target.hidden=true;return}
 target.hidden=false;
 const {wallet,name,balance,status,ownsFragment}=lookupResult;
 if(status&&(!wallet||status==="walletPending")){target.append(el("p",t(status),"note"));return}
 const holders=snapshot.holders?.holders||[];
 const rank=holders.findIndex(row=>row.wallet===wallet);
 const holder=holders[rank];
 const title=el("h3");
 title.append(walletIdentity(wallet,name||holder?.name,undefined,{holder:true,verifiedDomain:name,ownsFragment}));
 target.append(title);
 const value=balance??holder?.ludoman;
 const holding=el("p",value==null?t("walletBalanceUnknown"):t("walletBalance")+": "+format(value,4)+" LUDOMAN");
 if(balance==null&&holder)holding.append(" · "+stamp(snapshot.holders.asOf));
 target.append(holding);
 if(rank>=0){
   const entry=el("p",t("walletTop")+" ");
   entry.append(rankPosition(rank,snapshot.holders.previousRanks?.[wallet]));
   target.append(entry);
 }
 const recent=[...(snapshot.trades?.rows||[]),...burnRows()].filter(row=>row.wallet===wallet)
   .sort((a,b)=>b.time-a.time||a.tx.localeCompare(b.tx)).slice(0,5);
 target.append(el("h4",t("walletOperations")));
 if(!recent.length){target.append(el("p",t("walletNoOperations"),"note"));return}
 const entries=el("ul");
 for(const row of recent){
   const item=el("li");
   item.append(el("span",t(row.kind)+" · "+format(row.ludoman,4)+" LUDOMAN")," · ",tx(row));
   entries.append(item);
 }
 target.append(entries);
}

async function findWallet(event){
 event.preventDefault();
 lookupPending?.abort();
 lookupPending=null;
 const input=$("walletQuery").value.trim();
 let wallet=rawLookupAddress(input),name=null,balance=null,ownsFragment;
 if(!wallet&&!dnsPattern.test(input)){lookupResult={status:"walletInvalid"};renderLookup();return}
 const controller=new AbortController();lookupPending=controller;
 const timeout=setTimeout(()=>controller.abort(),12000);
 lookupResult={status:"walletPending"};renderLookup();
 try{
   if(!wallet){
     const query=input.toLowerCase();
     const cached=Object.keys(snapshot.identity?.byWallet||{}).find(key=>linkedDomain(key)===query)
       || (snapshot.holders?.asOf>=Date.now()/1000-day ? snapshot.holders.holders.find(row=>row.name===query)?.wallet : null);
     try{
       const record=await lookupData("/dns/"+encodeURIComponent(query)+"/resolve",controller.signal);
       wallet=rawLookupAddress(record?.wallet?.address||"");
     }catch(error){ if(!cached)throw error; wallet=cached; }
     if(!wallet){
       if(lookupPending===controller)lookupResult={status:"walletDomainMissing"};
       return;
     }
     name=query;
   }
   const account="/accounts/"+encodeURIComponent(wallet);
   const [jetton,nfts]=await Promise.allSettled([
     lookupData(account+"/jettons/"+MASTER,controller.signal),
     lookupData(account+"/nfts?"+new URLSearchParams({collection:fragmentCollection,limit:100}),controller.signal)
   ]);
   const record=jetton.value;
   const items=nfts.value?.nft_items;
   if(Array.isArray(items)){
     const ownsNumber=items.some(item=>item.verified===true && item.collection?.address===fragmentCollection &&
       item.owner?.address===wallet && wallet!=="0:"+"0".repeat(64));
     if(ownsNumber || items.length<100)ownsFragment=ownsNumber;
   }
   if(record&&rawLookupAddress(record.jetton?.address||"")===rawLookupAddress(MASTER)&&/^\d+$/.test(record.balance)){
     const decimals=Number(record.jetton.decimals);
     if(Number.isInteger(decimals)&&decimals>=0&&decimals<=30)balance=Number(record.balance)/10**decimals;
   }
 }catch{
   if(!wallet){
     if(lookupPending===controller)lookupResult={status:"walletNetwork"};
     return;
   }
 }finally{
   clearTimeout(timeout);
   if(lookupPending===controller){
     if(wallet)lookupResult={wallet,name,balance,ownsFragment};
     renderLookup();
   }
 }
}

function rankPosition(index,previous){
 const position=el("span",undefined,"position");
 position.append(el("span",String(index+1).padStart(2,"0")));
 if(Number.isInteger(previous)&&previous!==index+1){
   const delta=previous-index-1, up=delta>0;
   const badge=el("span",(up?"↑":"↓")+Math.abs(delta),"rankMove "+(up?"gained":"lost"));
   badge.setAttribute("aria-label",t(up?"rankGained":"rankLost")+" "+Math.abs(delta));
   position.append(badge);
 }
 return position;
}

function chart(){
 const section=snapshot.trades, model=marketCapSeries(snapshot,ranges[period],60,currency), {start,end,points}=model;
 const capWithUnit=n=>capFormat(n)+' '+currency;
 $('chartUnit').textContent=(lang==='ru'?'Оценка':'Estimate')+' · '+currency;
 $('lastPrice').textContent=model.latestCap!==null?capWithUnit(model.latestCap):'—';
 const change=$('capChange');change.textContent=model.change===null?'':(model.change>=0?'+':'')+format(model.change,2)+'%';
 change.className='capChange '+(model.change===null?'':model.change>=0?'capPositive':'capNegative');
 $('capPeriod').textContent=!points.length?t('no'):model.partial?t('capPartial')+' · '+t('since')+' '+stamp(points[0].time):t('periodNames')[period];
 $('capLow').textContent=model.low===undefined?'':t('capLow')+' · '+capWithUnit(model.low);
 $('capHigh').textContent=model.high===undefined?'':t('capHigh')+' · '+capWithUnit(model.high);
 const plot=$('plot');plot.replaceChildren();
 const width=Math.max(240,plot.clientWidth||800),left=8,right=width-76,top=20,bottom=184;
 const box=svg('svg',{viewBox:`0 0 ${width} 238`,preserveAspectRatio:'none',role:'group','aria-label':t('chart')});
 const x=time=>left+(time-start)/ranges[period]*(right-left);
 // The chart stays interactive; public technical readout has been removed.
 const colour=model.change===null||model.change>=0?'#38dda0':'#ff2020';
 $('market').style.setProperty('--chart-colour',colour);
 if(points.length){
   const pad=(model.high-model.low)*.12||Math.max(model.low*.015,1e-12);
   const min=Math.max(0,model.low-pad),max=model.high+pad;
   const y=value=>bottom-(value-min)/(max-min)*(bottom-top);
   for(let i=0;i<4;i++){
     const value=max-(max-min)*i/3, height=y(value);
     box.append(svg('path',{d:`M${left} ${height}H${right}`,stroke:'#344b5b','stroke-dasharray':'2 6'}));
     const label=svg('text',{x:right+9,y:height+4});label.textContent=capFormat(value,true);box.append(label);
   }
   const defs=svg('defs',{}),gradient=svg('linearGradient',{id:'capFill',x1:0,y1:0,x2:0,y2:1});
   gradient.append(svg('stop',{offset:'0%', 'stop-color':colour,'stop-opacity':'.26'}),svg('stop',{offset:'100%','stop-color':colour,'stop-opacity':'.015'}));defs.append(gradient);box.append(defs);
   const coords=points.map(p=>[x(p.time),y(p.cap)]),last=coords.at(-1),first=coords[0];
   box.append(svg('path',{d:`M${left} ${first[1]}H${right}`,stroke:'#7290a2','stroke-opacity':'.45','stroke-dasharray':'5 6'}));
   const line=coords.map((p,i)=>(i?'L':'M')+p.join(' ')).join(' ');
   box.append(svg('path',{d:line+`L${right} ${last[1]}L${right} ${bottom+2}L${first[0]} ${bottom+2}Z`,fill:'url(#capFill)'}));
   if(coords.length>1)box.append(svg('path',{d:line,fill:'none',stroke:colour,'stroke-width':2.7,'stroke-linejoin':'round','stroke-linecap':'round'}));
   if(last[0]<right)box.append(svg('path',{d:`M${last[0]} ${last[1]}H${right}`,stroke:colour,'stroke-width':1.5,'stroke-dasharray':'4 5',opacity:'.7'}));
   box.append(svg('circle',{cx:last[0],cy:last[1],r:4,fill:colour,stroke:'#e6fff5','stroke-width':1.5}));
   const cursorLine=svg('path',{stroke:'#c0d6e1','stroke-dasharray':'3 4',visibility:'hidden'});
   const cursor=svg('circle',{r:5,fill:'#10151c',stroke:colour,'stroke-width':3,visibility:'hidden'});box.append(cursorLine,cursor);
   let active=points.length-1;
   function inspect(i){
     active=i;const p=points[i],pos=coords[i];
     cursor.setAttribute('cx',pos[0]);cursor.setAttribute('cy',pos[1]);cursor.setAttribute('visibility','visible');
     cursorLine.setAttribute('d',`M${pos[0]} ${top}V${bottom}`);cursorLine.setAttribute('visibility','visible');
     // Cursor only: transaction details remain available in the operations feed.
   }
   inspect(active);
   box.setAttribute('tabindex','0');box.setAttribute('aria-description',t('pointHint'));
   function pointer(e){
     if(e.target.closest('.marker'))return;
     const rect=box.getBoundingClientRect(),at=(e.clientX-rect.left)*width/rect.width;
     inspect(coords.reduce((best,p,i)=>Math.abs(p[0]-at)<Math.abs(coords[best][0]-at)?i:best,0));
   }
   box.addEventListener('pointerdown',pointer);
   box.addEventListener('pointermove',e=>{if(e.pointerType==='mouse'||e.buttons)pointer(e)});
   box.addEventListener('keydown',e=>{
     if(e.target!==box||!['ArrowLeft','ArrowRight'].includes(e.key))return;
     e.preventDefault();inspect(Math.max(0,Math.min(active+(e.key==='ArrowLeft'?-1:1),points.length-1)));
   });
 }else{const label=svg('text',{x:left,y:100});label.textContent=t('no');box.append(label)}
 for(const r of burnRows().filter(r=>r.time>=start&&r.time<=end)){
   const g=svg('a',{href:'https://gram.org/tx/'+r.tx,class:'marker','aria-label':t('burn')+' '+format(r.ludoman)+' LUDOMAN'});
   const cx=Math.max(12,Math.min(right,x(r.time)));
   g.append(svg('rect',{x:cx-11,y:191,width:25,height:25,rx:6,fill:'#ffedd9'}));
   const icon=svg('text',{x:cx-7,y:209,style:'font-size:15px'});icon.textContent='🔥';g.append(icon);
   // Burn markers now link straight to the chain explorer without a readout.
   box.append(g);
 }
 const axisTime=seconds=>new Date(seconds*1000).toLocaleString(lang,period===0?{hour:'2-digit',minute:'2-digit'}:period===1?{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}:{day:'numeric',month:'short',year:'2-digit'});
 for(const [pos,time,anchor] of [[left,start,'start'],[width-3,end,'end']]){
   const label=svg('text',{x:pos,y:234,'text-anchor':anchor});label.textContent=axisTime(time);box.append(label);
 }
 plot.append(box);
 volumeBars(start,end,width,left,right);

}
/* Shared compact animated buying and selling icons. */
function trendMark(kind){
 const buy=kind==="buy";
 const mini=svg("svg",{viewBox:"0 0 52 28","class":"trendMini trend-"+kind,
   "aria-hidden":"true",focusable:"false"});
 const line=buy?"M3 24 L13 18 L21 20 L30 11 L39 13 L49 3":
   "M3 4 L13 9 L21 7 L30 17 L39 15 L49 25";
 const arrow=buy?"M41 3 L49 3 L49 11":"M41 25 L49 25 L49 17";
 mini.append(svg("path",{d:line,"class":"trendBase"}),
   svg("path",{d:line,"class":"trendLine"}),
   svg("path",{d:arrow,"class":"trendArrow"}));
 return mini;
}
function stats(){
 const trades=snapshot.trades,burns=snapshot.burns&&snapshot.zeroBurns?{...snapshot.burns,asOf:Math.min(snapshot.burns.asOf,snapshot.zeroBurns.asOf),rows:burnRows()}:snapshot.burns;
 const within=s=>(s?.rows||[]).filter(r=>r.time>s.asOf-day&&r.time<=s.asOf);
 const rows=within(trades), buys=rows.filter(r=>r.kind==="buy"), sells=rows.filter(r=>r.kind==="sell");
 const sum=(items,key)=>items.reduce((v,r)=>v+Number(r[key]),0);
 const count=s=>new Set(s.map(r=>r.wallet)).size;
 const values=[
   [t("buys"),buys.length,t("volumeUnit")+" · "+format(sum(buys,"ton"))+" GRAM",trades,"buy"],
   [t("sells"),sells.length,t("volumeUnit")+" · "+format(sum(sells,"ton"))+" GRAM",trades,"sell"],
   ["👛 "+t("people"),count(buys)+" / "+count(sells),t("buyers")+" / "+t("sellersLabel"),trades,""],
   [t("burnedTotal"),format(sum(within(burns),"ludoman")),t("events")+" · "+within(burns).length,burns,"burn"]];
 $("stats").replaceChildren(...values.map(([label,value,detail,source,cls])=>{
   const complete=source&&source.since<=source.asOf-day, item=el("div",undefined,"stat");
   const heading=el("span",undefined,"statHeading "+cls);
   heading.append(document.createTextNode(label));
   if(cls==="buy"||cls==="sell")heading.append(trendMark(cls));
   if(cls==="burn")heading.append(el("span","🔥","statFire"));
   item.append(heading,el("b",complete?value:"—"),el("small",complete?detail:source?t("partial"):t("no")));
   return item;
 }));
}
function row(first,sub,value,last){const a=el("div"),b=el("div"),d=el("div",undefined,"row");a.append(first,sub);b.append(value,last);d.append(a,b);return d}

/* Shared badge definitions: the same keys drive labels, filters and future observatories. */
const badgeFilterDefs=[
 ["og","OG"],["fragmentNumber","+888"],["digits","0000.ton"],
 ["author","author NFT"],["staking","JVault"],["vnuk","VNUK"],
 ["joystick","Joystick"],["phoenix","Phoenix"],["arni","ARNI"],
 ["napiwas","NAPIWAS"],["blueNft","🔵 NFT"],["burner","🔥 Burn"]
];
const selectedBadgeFilters=new Set();
function hasWalletBadge(wallet,key){
 if(key==="digits")return numericDomains(wallet).names.length>0;
 if(key==="fragmentNumber"){
   const item=snapshot.fragmentNumbers?.byWallet?.[wallet];
   return Boolean(item?.owns&&item.checkedAt>=Date.now()/1000-2*day);
 }
 if(key==="og"){
   const activated=snapshot.identity?.byWallet?.[wallet]?.activated;
   if(!activated)return false;
   const date=new Date(activated*1000),fifth=new Date(date);
   fifth.setUTCFullYear(date.getUTCFullYear()+5);
   if(fifth.getUTCMonth()!==date.getUTCMonth())fifth.setUTCDate(0);
   return Date.now()>fifth.getTime();
 }
 if(key==="burner")return (burnTotals?.get(wallet)||0n)>=1000n*10n**9n;
 const sources=snapshot.badges?.sources;
 const valid=k=>sources?.[k]?.asOf>=Date.now()/1000-24*3600&&Boolean(sources[k].wallets?.[wallet]);
 return valid(key)||((key==="vnuk"||key==="joystick")&&valid(key+"Nft"));
}
function renderBadgeFilterList(){
 const list=$("badgeFilterList");
 if(!list)return;
 const needle=($("badgeFilterSearch")?.value||"").trim().toLocaleLowerCase();
 list.replaceChildren();
 for(const [key,label] of badgeFilterDefs){
   if(!label.toLocaleLowerCase().includes(needle))continue;
   const item=el("label",undefined,"badgeFilterItem");
   const check=el("input");check.type="checkbox";check.checked=selectedBadgeFilters.has(key);
   check.onchange=()=>{if(check.checked)selectedBadgeFilters.add(key);else selectedBadgeFilters.delete(key);expanded=false;listOperations();};
   item.append(check,el("span",label));list.append(item);
 }
 $("badgeFilterCount").textContent=selectedBadgeFilters.size?"("+selectedBadgeFilters.size+")":"";
}
function listOperations(){list();}

function list(){
 const kinds=["all","buy","sell","burn"];
 select("filters",[t("filterAll"),t("buys"),t("sells"),t("burnCount")],kinds.indexOf(feedKind),i=>{feedKind=kinds[i];expanded=false;list()});
 renderBadgeFilterList();
 const large=$("largeTrades").checked,threshold=$("minTradeSize").valueAsNumber;
 $("minTradeSize").disabled=!large;
 const combined=[...(snapshot.trades?.rows||[]),...burnRows()]
  .filter(r=>!large||(r.kind!=="burn"&&Number.isFinite(threshold)&&threshold>=0&&Number(r.ton)>=threshold))
  .filter(r=>(feedKind==="all"||r.kind===feedKind)
    &&(!$("feedDomains").checked||hasDomainBadge(r.wallet))
    &&[...selectedBadgeFilters].every(key=>hasWalletBadge(r.wallet,key)))
  .sort((a,b)=>b.time-a.time||a.tx.localeCompare(b.tx)).slice(0,50);
 const visible=expanded?combined:combined.slice(0,10);
 $("feed").replaceChildren(...visible.map(r=>{
   const item=el("article",undefined,"row operationRow trade-"+r.kind);
   const header=el("div",undefined,"opHeader");
   const title=el("strong",r.method==="zero"?t("toZero"):t(r.kind),"opKind "+r.kind);
   const date=el("time",stamp(r.time),"opDate");
   date.dateTime=new Date(r.time*1000).toISOString();
   const titleGroup=el("span",undefined,"opTitleGroup");
   titleGroup.append(title);
   if(r.kind==="buy"||r.kind==="sell"){
     titleGroup.append(trendMark(r.kind));
   }
   header.append(titleGroup,date);
   const amounts=el("div",undefined,"opAmounts");
   const token=el("div",undefined,"opAmount opToken");
   token.append(el("strong",format(r.ludoman),"opAmountValue"),el("small","LUDOMAN","opAmountUnit"));
   const gram=el("div",undefined,"opAmount opGram");
   const hasGram=r.ton!=null&&Number(r.ton)>0;
   gram.append(el("strong",hasGram?format(r.ton):"—","opAmountValue"),el("small","GRAM","opAmountUnit"));
   amounts.append(token,gram);
   const footer=el("div",undefined,"opFooter");
   const wallet=el("div",undefined,"opWallet");
   wallet.append(walletIdentity(r.wallet,r.name,r.kind,{activity:true}));
   const transaction=link("https://gram.org/tx/"+r.tx,lang==="ru"?"Транзакция":"Transaction");
   transaction.className="opTransaction";
   transaction.title=r.tx;
   transaction.target="_blank";
   transaction.rel="noopener noreferrer";
   footer.append(wallet,transaction);
   item.append(header,amounts,footer);
   if(r.kind==="buy"||r.kind==="sell"){
     const watermark=el("div",undefined,"operationWatermark");
     watermark.setAttribute("aria-hidden","true");
     for(let i=0;i<5;i++)watermark.append(brandMarkNode("ludoman"));
     item.prepend(watermark);
   }
   return item;
 }));
 if(!combined.length)$("feed").append(el("p",t(large?"noLargeTrades":$("feedDomains").checked||selectedBadgeFilters.size?"noneTagged":"none"),"empty"));
 const more=$("more");
 more.hidden=combined.length<=10;
 more.setAttribute("aria-expanded",String(expanded));
 more.setAttribute("aria-controls","feed");
 more.textContent=expanded?t("less")+" ↑":t("more")+" ("+(combined.length-10)+") ↓";
}
function rankedSellers(source){
 const groups=new Map();
 const cut=(source?.asOf||0)-sellerDays*day;
 for(const row of source?.rows||[]){
   if(row.kind!=="sell"||row.time<=cut||row.time>source.asOf)continue;
   const group=groups.get(row.wallet)||{...row,units:0n,count:0};
   group.units+=tokenUnits(row.ludoman);
   group.count++;
   groups.set(row.wallet,group);
 }
 return [...groups.values()].sort((a,b)=>{
   if(a.units!==b.units)return a.units>b.units?-1:1;
   return a.wallet<b.wallet?-1:1;
 });
}
function serviceRole(wallet){
 const role=snapshot.identity?.byWallet?.[wallet]?.role;
 return typeof role==="string"&&role.trim()?role.trim():null;
}
function ranks(){
 const lastActivity=lastTradeByWallet();
 const isHolder=ranking==="holders",isService=ranking==="services";
 const source=ranking==="sellers"?snapshot.trades:snapshot.holders;
 const views=["holders","sellers","services"];
 select("views",[t("holders"),t("sellers"),t("services")],views.indexOf(ranking),i=>{ranking=views[i];ranks()});
 $("sellerPeriods").replaceChildren();
 if(!isHolder&&!isService)select("sellerPeriods",t("dayLabels"),[1,7,30].indexOf(sellerDays),i=>{sellerDays=[1,7,30][i];ranks()});
 const data=(isHolder||isService?(source?.holders||[]).filter(r=>Boolean(serviceRole(r.wallet))===isService):
   rankedSellers(source).filter(r=>!serviceRole(r.wallet))).slice(0,20);
 // Historical ranks mixed services and people; do not display misleading movements.
 const previous=null;
 $("rank").replaceChildren(...data.map((r,i)=>{
   const title=el("b");
   title.append(rankPosition(i,previous?.[r.wallet]),walletIdentity(r.wallet,r.name,(isHolder||isService)?lastActivity.get(r.wallet):"sell",{holder:isHolder||isService}));
   const entry=row(title,el("small",(isHolder||isService)?t("balance"):t("sold")),
     el("b",format((isHolder||isService)?r.ludoman:Number(r.units)/1e9)+" LUDOMAN"),
     el("small",(isHolder||isService)?format(r.share,4)+"%":(lang==="ru"?"Сделок: ":"Trades: ")+countFormat(r.count)));
   entry.classList.add("rankingRow");
   if(i<10&&isHolder){
     entry.classList.add("diamondHands");
     entry.firstElementChild.prepend(el("span","💎 Diamond Hands","rankHonor diamondHonor"));
   }else if(i<10&&!isService&&!isHolder&&(sellerDays===7||sellerDays===30)){
     entry.classList.add("bestSellers");
     entry.firstElementChild.prepend(el("span","🔁 Best Sellers","rankHonor bestHonor"));
   }
   return entry;
 }));
 if(!data.length)$("rank").append(el("p",source?t("none"):t("no"),"empty"));
}

/* Self-contained brand marks: real Ludoman art and inline vector / letter marks.
   No third-party fonts, icon CDNs, scripts or external UI dependencies. */
const brandLabels={ludoman:"L",ton:"◆",gram:"G",kito:"K",usdt:"₮",usda:"U",rton:"R",
  telegram:"",x:"",github:"GH",ston:"S",dedust:"D",tonco:"C",gecko:"G",
  gramorg:"◎",tonviewer:"TV",dexscreener:"DX",tonraffles:"TR",
  jvault:"JV",getgems:"GG",fragment:"F",web:"W",explorer:"↗"};
/* Owner-approved source artwork is embedded in index.html, with no network calls. */
function applyApprovedBrand(node,kind){
 const atlas=typeof window==="object"?window.OBSERVATORY_BRAND_ATLAS:null;
 const pos=atlas?.positions?.[kind];
 if(!atlas?.image||!Array.isArray(pos))return false;
 const artwork=el("span",undefined,"brandTile");
 artwork.style.backgroundImage='url("'+atlas.image+'")';
 artwork.style.backgroundSize=(atlas.cols*100)+"% "+(atlas.rows*100)+"%";
 artwork.style.backgroundPosition=(100*pos[0]/(atlas.cols-1))+"% "+(100*pos[1]/(atlas.rows-1))+"%";
 node.classList.add("hasApprovedArtwork");
 node.append(artwork);
 return true;
}
function brandMarkNode(kind){
 const icon=el("span",undefined,"brandGlyph brand-"+kind);
 icon.setAttribute("aria-hidden","true");
 // Only approved and locally embedded brand graphics may replace placeholders.
 if(applyApprovedBrand(icon,kind))return icon;
 const approved=typeof window==="object"?window.OBSERVATORY_ICON_PACK?.[kind]:null;
 if(approved){
   const logo=el("img");
   logo.alt="";
   logo.width=18;
   logo.height=18;
   logo.loading="eager";
   logo.decoding="async";
   logo.src=approved;
   icon.append(logo);
   return icon;
 }
 if(kind==="telegram"){
   const plane=svg("svg",{viewBox:"0 0 24 24",fill:"none","aria-hidden":"true"});
   plane.append(svg("path",{d:"M21 3 L3 10.5 L10 13.4 L12.9 21 L21 3 Z M10 13.4 L21 3 L15.1 16.1",stroke:"currentColor","stroke-width":"1.8","stroke-linejoin":"round","stroke-linecap":"round"}));
   icon.append(plane);
 } else if(kind==="x"){
   const mark=svg("svg",{viewBox:"0 0 24 24",fill:"none","aria-hidden":"true"});
   mark.append(svg("path",{d:"M4 3 L9 3 L20 21 L15 21 Z M20 3 L13.1 11.1 M10.9 13.8 L4 21",stroke:"currentColor","stroke-width":"1.8","stroke-linecap":"round"}));
   icon.append(mark);
 }else{
   icon.textContent=brandLabels[kind]||"•";
 }
 return icon;
}
function markFromLink(anchor){
 if(anchor.closest("#supply")&&anchor.querySelector("#stakingTotal"))return "jvault";
 let host;
 try{host=new URL(anchor.href,location.href).hostname.toLowerCase()}catch{return null}
 if(host==="t.me"||host==="telegram.me")return"telegram";
 if(host==="x.com"||host==="twitter.com")return"x";
 if(host==="github.com")return"github";
 if(host.endsWith("ston.fi"))return"ston";
 if(host.endsWith("dedust.io"))return"dedust";
 if(host.includes("tonco"))return"tonco";
 if(host.includes("geckoterminal"))return"gecko";
 if(host==="gram.org")return"gramorg";
 if(host.includes("tonviewer"))return"tonviewer";
 if(host.includes("dexscreener"))return"dexscreener";
 if(host.includes("tonraffles"))return"tonraffles";
 if(host.includes("jvault"))return"jvault";
 if(host.includes("getgems"))return"getgems";
 if(host.includes("fragment.com"))return"fragment";
 if(host.includes("ludoman"))return"ludoman";
 return null;
}
function decorateBrandLinks(){
 const headerIcon=document.querySelector(".brand .brandMark");
 if(headerIcon&&!headerIcon.querySelector(".brandTile"))applyApprovedBrand(headerIcon,"ludoman");
 // +888 and author NFT stay legible; their service artwork appears in the badge guide.
 for(const item of document.querySelectorAll("[data-brand]")){
   if(!item.querySelector(".brandGlyph"))item.prepend(brandMarkNode(item.dataset.brand));
 }
 for(const item of document.querySelectorAll("#wallets .badgeLegend dt[data-badge-key]")){
   if(item.querySelector(".projectBadge"))continue;
   const key=item.dataset.badgeKey;
   const badge=el("span",undefined,"projectBadge badgePreview "+key);
   if(key==="napiwas"){
     const beer=el("span",undefined,"beerIcon");
     beer.setAttribute("aria-hidden","true");
     badge.append(beer);
   }else{
     const icon=$("badge-icon-"+key)?.content.firstElementChild?.cloneNode(true);
     if(icon)badge.append(icon);
   }
   badge.setAttribute("aria-hidden","true");
   item.prepend(badge);
 }
 const legendBrands={"+888":"fragment","author NFT":"getgems","JVault":"jvault"};
 for(const label of document.querySelectorAll("#wallets .badgeLegend dt")){
  const kind=legendBrands[label.textContent.trim()];
  if(kind&&!label.querySelector(".brandGlyph"))label.prepend(brandMarkNode(kind),document.createTextNode(" "));
 }
 const selector=".introLinks a,.resourceList a,#pools .poolActions a,#pools .poolSources a,.supplyGrid a";
 for(const anchor of document.querySelectorAll(selector)){
   if(anchor.querySelector(".brandGlyph"))continue;
   const brand=markFromLink(anchor);
   if(!brand)continue;
   anchor.classList.add("brandedLink");
   anchor.prepend(brandMarkNode(brand));
   if(anchor.hostname&&anchor.hostname!==location.hostname){
     anchor.target="_blank";
     anchor.rel="noopener noreferrer";
   }
 }
 for(const card of document.querySelectorAll("#pools .poolCard")){
   const descriptor=card.querySelector("p")?.textContent?.toLowerCase()||"";
   card.classList.remove("dex-dedust","dex-ston","dex-tonco","dex-mixed");
   const hasDedust=descriptor.includes("dedust");
   const hasSton=descriptor.includes("ston.fi");
   if(hasDedust&&hasSton)card.classList.add("dex-mixed");
   else if(descriptor.includes("tonco"))card.classList.add("dex-tonco");
   else if(hasDedust)card.classList.add("dex-dedust");
   else if(hasSton)card.classList.add("dex-ston");
   // Identify the actual DEX on its pool card, even when actions link to a chart.
   const venueLine=card.querySelector("p");
   if(venueLine&&!venueLine.querySelector(".dexMarks")){
     const venueNames=[];
     if(hasDedust)venueNames.push("dedust");
     if(hasSton)venueNames.push("ston");
     if(descriptor.includes("tonco"))venueNames.push("tonco");
     if(venueNames.length){
       const marks=el("span",undefined,"dexMarks");
       marks.setAttribute("aria-hidden","true");
       for(const venue of venueNames)marks.append(brandMarkNode(venue));
       venueLine.prepend(marks,document.createTextNode(" "));
     }
   }
   // Display recognisable token marks rather than text alone. Preserve symbols.
   const name=card.querySelector("h3");
   if(name&&!name.querySelector(".brandGlyph")){
     const label=name.textContent;
     const match=label.match(/^(LUDOMAN)\s*\/\s*(.+)$/i);
     if(match){
       const quote=match[2].replace(/\s*\(TON\)\s*$/i,"").trim().toLowerCase();
       const tokenKind=brandLabels[quote]!==undefined?quote:(quote==="ton"?"ton":null);
       name.replaceChildren(brandMarkNode("ludoman"),document.createTextNode(" LUDOMAN / "));
       if(tokenKind)name.append(brandMarkNode(tokenKind),document.createTextNode(" "+match[2]));
       else name.append(document.createTextNode(match[2]));
     }
   }
 }
}

function renderPools(){
  const section=snapshot.pools;
  const grid=$("discoveredPools");
  grid.replaceChildren();
  const labels={
    pool:"Пул", analytics:"Аналитика", contract:"Контракт", liquidity:"Ликвидность", checked:"Проверено по GeckoTerminal"
  };
  const english={pool:"Pool", analytics:"Analytics", contract:"Contract", liquidity:"Liquidity", checked:"Checked via GeckoTerminal"};
  const words=lang==="ru"?labels:english;
  $("poolChecked").textContent=section?.asOf?words.checked+" · "+stamp(section.asOf):"";
  const indexed=new Map((section?.rows||[]).map(pool=>[rawLookupAddress(pool.address),pool]));
  for(const card of document.querySelectorAll("#pools .knownPools .poolCard")){
    card.querySelector(".poolLiquidity")?.remove();
    const entries=[];
    for(const anchor of card.querySelectorAll("a")){
      const url=new URL(anchor.href);
      if(url.hostname!=="www.geckoterminal.com" && url.hostname!=="gram.org")continue;
      const address=rawLookupAddress(url.pathname.split("/").pop());
      const pool=indexed.get(address);
      if(!pool)continue;
      indexed.delete(address);
      if(pool.liquidityUsd!=null)entries.push("$"+format(pool.liquidityUsd,2));
    }
    if(entries.length)card.append(el("p",words.liquidity+" · "+entries.join(" / "),"poolLiquidity"));
  }
  for(const pool of indexed.values()){
    const address=rawLookupAddress(pool.address);
    if(!address)continue;
    const card=el("article",undefined,"poolCard");
    card.append(el("h3","LUDOMAN / "+pool.symbol),el("p",pool.dex));
    const actions=el("div",undefined,"poolActions");
    const dex=/dedust/i.test(pool.dex)?"dedust":/ston/i.test(pool.dex)?"ston":null;
    if(dex)actions.append(link("https://"+(dex==="dedust"?"dedust.io":"app.ston.fi")+"/pools/"+encodeURIComponent(pool.address),words.pool));
    actions.append(link("https://www.geckoterminal.com/ton/pools/"+encodeURIComponent(pool.address),words.analytics),
      link("https://gram.org/address/"+encodeURIComponent(pool.address),words.contract));
    card.append(actions);
    if(pool.liquidityUsd!=null)card.append(el("p",words.liquidity+" · $"+format(pool.liquidityUsd,2),"poolLiquidity"));
    grid.append(card);
  }
  grid.hidden=!grid.childElementCount;
}
function renderSupply(){
  const frozen=snapshot.vesting?.reserved;
  const principal=snapshot.staking?.principal;
  const estimate=marketCapSeries(snapshot,30*day,60,"USD");
  const supply=Number(snapshot.holders?.totalSupply);
  const latest=estimate.latest;
  const valid=Number.isFinite(estimate.latestCap)&&estimate.latestCap>0
    &&Number.isFinite(supply)&&supply>0
    &&latest?.time && snapshot.trades?.asOf-latest.time<=2*day;
  const price=valid?estimate.latestCap/supply:null;
  for(const [amount,totalId,usdId] of [
    [frozen,"frozenTotal","frozenUsd"],[principal,"stakingTotal","stakingUsd"]]){
    const units=Number(amount);
    $(totalId).textContent=amount==null?"—":format(units)+" LUDOMAN";
    const usd=price!=null&&Number.isFinite(units)&&units>=0?units*price:null;
    $(usdId).textContent=usd===null?"—":"≈ $"+format(usd)+" USD";
    $(usdId).title=t("supplyUsdHint");
  }
}
function render(){document.documentElement.lang=lang;document.querySelectorAll("[data-t]").forEach(n=>n.textContent=t(n.dataset.t));for(const l of ["ru","en"]){$(l).classList.toggle("on",l===lang);$(l).setAttribute("aria-pressed",l===lang);$(l).onclick=()=>{lang=l;try{localStorage.setItem("ludoman-lang",l)}catch{}render()}}
 $("currency").setAttribute("aria-label",lang==="ru"?"Валюта капитализации":"Market cap currency");
 $("periods").setAttribute("aria-label",lang==="ru"?"Период графика":"Chart period");
 select("currency",["GRAM","USD"],currency==="USD"?1:0,i=>{
   currency=i?"USD":"GRAM";
   try{localStorage.setItem("ludoman-currency",currency)}catch{}
   render();
 });
 select("periods",t("periodNames"),period,i=>{period=i;render()});$("badgeFilterSearch").placeholder=t("filterSearchPlaceholder");$("copy").textContent=t("copy");$("contract").href="https://gram.org/jetton/"+MASTER;$("contractAddress").textContent=MASTER;updateBurnTotals();chart();stats();list();ranks();renderLookup();renderSupply();renderPools();decorateBrandLinks();renderSyncStatus()}
$("copy").onclick=async()=>{try{await navigator.clipboard.writeText(MASTER);$("copy").textContent=t("copied")}catch{window.prompt(t("copy"),MASTER)}};
$("walletSearchForm").onsubmit=findWallet;
$("largeTrades").onchange=$("minTradeSize").oninput=()=>{expanded=false;list()};
$("feedDomains").onchange=()=>{expanded=false;list()};
$("more").onclick=()=>{expanded=!expanded;list()};
$("badgeFilterToggle").onclick=()=>{
 const panel=$("badgeFilterPanel");panel.hidden=!panel.hidden;
 $("badgeFilterToggle").setAttribute("aria-expanded",String(!panel.hidden));
 if(!panel.hidden)$("badgeFilterSearch").focus();
};
$("badgeFilterSearch").oninput=renderBadgeFilterList;
$("clearBadgeFilters").onclick=()=>{
 selectedBadgeFilters.clear();$("badgeFilterSearch").value="";
 $("feedDomains").checked=false;$("largeTrades").checked=false;
 expanded=false;list();
};
window.addEventListener("resize",chart);render();
function renderSyncStatus(){
 const ru=lang==='ru', now=Date.now()/1000;
 const times=['trades','burns','holders'].map(k=>snapshot[k]?.asOf||0);
 const asOf=Math.min(...times), minutes=Math.max(0,Math.floor((now-asOf)/60));
 let age=minutes<1?(ru?'только что':'just now'):minutes<60?(ru?`${minutes} мин. назад`:`${minutes} min ago`):(ru?`${Math.floor(minutes/60)} ч ${minutes%60} мин. назад`:`${Math.floor(minutes/60)}h ${minutes%60}m ago`);
 const fresh=asOf?(ru?'Данные обновлены '+age:'Data updated '+age):(ru?'Нет полного снимка данных':'Complete snapshot unavailable');
 const loading=syncState.phase==='loading', failed=syncState.phase==='error';
 $('syncStatus').textContent=loading?(ru?'Проверяем обновления…':'Checking for updates…'):failed?(ru?'Не удалось загрузить свежие данные':'Could not load fresh data'):fresh;
 const warning=!asOf || minutes>=150 || (snapshot.errors||[]).length>0;
 $('syncStatus').className=failed||warning?'syncWarning':'';
 let detail=loading||failed?fresh:warning?(ru?'Часть данных устарела. Ожидаем новый снимок.':'Some data is old. Waiting for a new snapshot.'):(ru?'Автопроверка каждые 5 минут':'Checks every 5 minutes');
 if(failed) detail+=' · '+(ru?'Показана сохранённая копия. Повторим проверку автоматически.':'Showing the saved copy. We will retry automatically.');
 if(syncState.checkedAt&&!loading&&!failed) detail+=' · '+(ru?'Проверено в ':'Checked at ')+new Date(syncState.checkedAt).toLocaleTimeString(lang,{hour:'2-digit',minute:'2-digit'});
 $('syncDetail').textContent=detail;
 $('syncStatus').title=asOf?stamp(asOf):'';
 $('refreshData').textContent=loading?(ru?'Загрузка…':'Loading…'):(ru?'Обновить':'Refresh');
 $('refreshData').disabled=loading;
}
const refresh=createSnapshotLoader({
 getSnapshot:()=>snapshot,
 applySnapshot:next=>{
  for(const key of ["zeroBurns","identity","fragmentNumbers","pools","vesting","staking"]){
    if(snapshot[key]&&(!next[key]||snapshot[key].asOf>next[key].asOf))next[key]=snapshot[key];
  }
  snapshot=next;
  render();
 },
 onState:state=>{syncState={...syncState,...state};renderSyncStatus()}
});
$('refreshData').onclick=()=>refresh();
refresh();
setInterval(()=>{if(!document.hidden)refresh()},300000);
setInterval(renderSyncStatus,60000);
window.addEventListener('online',refresh);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});

const jumps=Array.from(document.querySelectorAll("#nav a"));
function activeSection(){
 const y=window.scrollY+Math.min(window.innerHeight*.35,220);
 const narrow=window.matchMedia("(max-width:800px)").matches;
 const hash=window.location.hash;
 let target=jumps[0];
 for(const jump of jumps){
   const section=document.querySelector(jump.hash);
   if(section.offsetTop>y)continue;
   if(!narrow&&jump.hash==="#wallets"&&hash!=="#wallets")continue;
   target=jump;
 }
 for(const jump of jumps){
   jump.classList.toggle("on",jump===target);
   if(jump===target)jump.setAttribute("aria-current","location");else jump.removeAttribute("aria-current");
 }
}
window.addEventListener("scroll",activeSection,{passive:true});
window.addEventListener("hashchange",activeSection);
activeSection();
