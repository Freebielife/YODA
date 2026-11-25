import test from 'node:test';
import assert from 'node:assert/strict';
import worker,{selectDueProjects,validateProject,dispatchDue} from '../src/index.mjs';
import {projects} from '../src/projects.mjs';
const fixture=(extra={})=>({id:'sample',owner:'ExampleOrg',repo:'SampleToken',workflow:'update.yml',ref:'main',everyMinutes:30,phaseMinutes:0,enabled:true,...extra});
const now='2026-11-22T12:00:00Z';
test('template registry is empty and does not dispatch any existing site',async()=>{
 assert.deepEqual(projects,[]);
 assert.deepEqual(await dispatchDue({scheduledTime:now,token:'',fetcher:()=>{throw Error('network should not run')}}),[]);
});
test('30 minute projects use independent staggered phases',()=>{
 const registry=[fixture(),fixture({id:'second',phaseMinutes:10})];
 assert.deepEqual(selectDueProjects(now,registry).map(p=>p.id),['sample']);
 assert.deepEqual(selectDueProjects('2026-11-22T12:10:00Z',registry).map(p=>p.id),['second']);
 assert.deepEqual(selectDueProjects('2026-11-22T12:20:00Z',registry),[]);
 assert.deepEqual(selectDueProjects('2026-11-22T12:30:00Z',registry).map(p=>p.id),['sample']);
});
test('invalid cadence, path injection and duplicate IDs are rejected',()=>{
 assert.throws(()=>validateProject(fixture({everyMinutes:17})),/everyMinutes/);
 assert.throws(()=>validateProject(fixture({owner:'../unsafe'})),/owner/);
 assert.throws(()=>selectDueProjects(now,[fixture(),fixture()]),/Duplicate/);
});
test('disabled project never runs',()=>assert.deepEqual(selectDueProjects(now,[fixture({enabled:false})]),[]));
test('explicit project dispatch targets only its own repository',async()=>{
 const calls=[];
 const result=await dispatchDue({scheduledTime:now,registry:[fixture()],token:'synthetic-test-secret',fetcher:async(url,init)=>{calls.push({url,init});return {ok:true,status:204}}});
 assert.deepEqual(result,['sample']);
 assert.equal(calls.length,1);
 assert.equal(calls[0].url,'https://api.github.com/repos/ExampleOrg/SampleToken/actions/workflows/update.yml/dispatches');
 assert.equal(calls[0].init.headers.Authorization,'Bearer synthetic-test-secret');
 assert.deepEqual(JSON.parse(calls[0].init.body),{ref:'main'});
});
test('due configured projects require credentials',async()=>{
 await assert.rejects(()=>dispatchDue({scheduledTime:now,registry:[fixture()],token:'',fetcher:()=>{throw Error('must not send')}}),/GITHUB_ACTIONS_TOKEN/);
});
