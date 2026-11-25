/* Estimated valuation in GRAM or USD, with no external chart library. */
(function(root){
  function marketCapSeries(snapshot, duration, buckets=60, currency="GRAM"){
    const supply=Number(snapshot.holders?.totalSupply), end=Number(snapshot.trades?.asOf), start=end-duration;
    const validSupply=Number.isFinite(supply)&&supply>0;
    const rates=snapshot.rates?.rows||[];
    function usdAt(time){
      let start=0,end=rates.length;
      while(start<end){
        const middle=(start+end)>>1;
        if(rates[middle][0]<=time)start=middle+1;
        else end=middle;
      }
      const rate=rates[start-1];
      return rate&&time-rate[0]<=2*86400?rate[1]:null;
    }
    const rows=(snapshot.trades?.rows||[]).filter(r=>
      (!r.dex||r.dex==="STON.fi")&&Number.isFinite(r.time)&&r.time<=end&&
      Number.isFinite(Number(r.ludoman))&&Number(r.ludoman)>0&&Number.isFinite(Number(r.ton))&&Number(r.ton)>0)
      .slice().sort((a,b)=>a.time-b.time||(a.lt||"").localeCompare(b.lt||"",undefined,{numeric:true})||a.tx.localeCompare(b.tx));
    function value(row,time=row.time){
      const rate=currency==="USD"?usdAt(time):1;
      return rate===null?null:Number(row.ton)/Number(row.ludoman)*supply*rate;
    }
    const latest=rows.at(-1);
    const result={supply,end,start,latest,latestCap:validSupply&&latest?value(latest,end):null,points:[],change:null,partial:true,tradeCount:0};
    if(!validSupply||!Number.isFinite(end)||!Number.isFinite(duration)||duration<=0) return result;
    const before=rows.filter(r=>r.time<=start).at(-1);
    const within=rows.filter(r=>r.time>=start);
    const points=within.map(row=>({time:row.time,cap:value(row),row})).filter(point=>point.cap!==null);
    result.tradeCount=within.length;
    const startingCap=before?value(before,start):null;
    const missingRate=points.length<within.length;
    if(before&&before.time<start&&startingCap!==null) points.unshift({time:start,cap:startingCap,row:before});
    if(currency==="USD"&&latest&&latest.time<end&&result.latestCap!==null){
      points.push({time:end,cap:result.latestCap,row:latest});
    }
    if(!points.length)return result;
    result.partial=startingCap===null || snapshot.trades.since>start || missingRate;
    result.low=points.reduce((min,p)=>Math.min(min,p.cap),Infinity); result.high=points.reduce((max,p)=>Math.max(max,p.cap),0);
    const first=points[0], last=points.at(-1);
    if(points.length>1||(!result.partial&&before)) result.change=(last.cap/first.cap-1)*100;
    // Keep each interval's first, last, low and high so a large trade cannot disappear.
    const groups=new Map();
    for(const p of points){
      const key=Math.floor((p.time-start)/duration*buckets);
      if(!groups.has(key))groups.set(key,[]);
      groups.get(key).push(p);
    }
    for(const group of groups.values()){
      const picked=new Set([group[0],group.at(-1),group.reduce((a,b)=>a.cap<b.cap?a:b),group.reduce((a,b)=>a.cap>b.cap?a:b)]);
      result.points.push(...group.filter(p=>picked.has(p)));
    }
    return result;
  }
  if(typeof module!=='undefined'&&module.exports)module.exports={marketCapSeries};
  else root.marketCapSeries=marketCapSeries;
})(globalThis);
