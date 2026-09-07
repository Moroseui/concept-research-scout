"""Campaign artifacts through the existing protected three-stage model broker.

This adapter supplies no credential, admission grant, scheduler or patient runner.
A trusted caller must bind the completion and source and use the protected socket.
The shared campaign pipeline still checks its scientific context and opposing
families. One author/reviewer round leaves the third stage for a disposition.
"""
import hashlib
import json
from pathlib import Path
import re
from orchestrator.campaign_pipeline import MODES, execute
from orchestrator.handover_runtime import request_broker
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.public_export import text


class BrokerStages:
    def __init__(self, socket, event, packet, *, client=request_broker):
        self.socket=socket;self.event=event;self.packet=packet;self.client=client
        self.completed=[];self.receipts={};self.mode=None

    def call(self, stage, prompt):
        expected=('continuation','review','disposition')
        if len(self.completed)>=3 or stage!=expected[len(self.completed)]:
            raise ValueError('HOSTED_CAMPAIGN_STAGE_ORDER_OR_BOUND')
        response=self.client(self.socket,'model_stage',{'event':self.event,'stage':stage,
                                                      'packet':self.packet,'prompt':prompt})
        if response.get('status')!='COMPLETE':
            raise ValueError('HOSTED_CAMPAIGN_BLOCKED_RECONCILE_NO_RETRY')
        answer=response['answer'];receipt=response['receipt']
        text(answer)
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        if (receipt.get('requested_model')!=model or receipt.get('returncode')!=0
                or receipt.get('answer_sha256')!=hashlib.sha256(answer.encode()).hexdigest()
                or not re.fullmatch('[0-9a-f]{64}',receipt.get('operating_context_sha256',''))):
            raise ValueError('HOSTED_CAMPAIGN_RECEIPT_BINDING')
        if stage=='review' and receipt.get('actual_model')!=model:
            raise ValueError('HOSTED_CAMPAIGN_REVIEW_MODEL')
        self.receipts[stage]={'receipt':receipt,'duplicate':response.get('duplicate')}
        self.completed.append(stage)
        return answer,receipt

    def __call__(self, sc, directory, family, stage, body, names):
        index=len(self.completed)
        if index>=2 or family!=('codex','claude')[index]:
            raise ValueError('HOSTED_CAMPAIGN_AUTHOR_REVIEW_BOUND')
        if (index==0 and (stage not in ('campaign_readiness','campaign_discuss')
                or names!=MODES[stage.removeprefix('campaign_')])) or (index==1 and (names!=['review.json'] or stage!='campaign_'+str(self.mode)+'_review')):
            raise ValueError('HOSTED_CAMPAIGN_ARTIFACT_SCOPE')
        if index==0:self.mode=stage.removeprefix('campaign_')
        prompt=('Produce the requested scientific artifact contents as ONE JSON object whose keys are exactly '
                +json.dumps(names)+'. Each value must be a string containing that file body. '
                'The controller writes these checked files; do not use tools or claim to have written them. '
                'Keep proposals distinct from ratification and launch authority.\n'+body)
        answer,receipt=self.call(('continuation','review')[index],prompt)
        # Accept a single JSON fence for compatibility with the broker's Markdown
        # transport; reject surrounding prose or any executable transport wrapper.
        raw=answer.strip()
        match=re.fullmatch(r'```(?:json)?\s*\n(.*)\n```',raw,re.S)
        if match:raw=match.group(1)
        files=json.loads(raw)
        if not isinstance(files,dict) or set(files)!=set(names) or any(not isinstance(v,str) for v in files.values()):raise ValueError('HOSTED_CAMPAIGN_FILE_SCHEMA')
        for name,content in files.items():
            text(content)
            if not content.strip():raise ValueError('HOSTED_CAMPAIGN_EMPTY_ARTIFACT')
        # The private original broker receipts remain authoritative. These are
        # validated transport-derived provenance, not manufactured model receipts.
        record={'family_effective':family,'exit_class':'ok','ci':False,
                'runner':{'adapter':'protected-hosted-campaign-v1'},
                'requested_model':receipt['requested_model'],'actual_model':receipt.get('actual_model'),
                'model_receipt_sha256':hashlib.sha256(encoded(receipt)).hexdigest(),
                'operating_context_sha256':receipt['operating_context_sha256'],
                'original_protocol_private':True,'event':self.event,
                'packet_sha256':hashlib.sha256(encoded(self.packet)).hexdigest(),
                'broker_duplicate':self.receipts[('continuation','review')[index]]['duplicate']}
        for name,content in files.items():immutable(Path(directory)/name,content.encode())
        immutable(Path(directory)/(stage+'.hosted-provenance.json'),encoded(record))
        return record


def run_pipeline(sc, mode, request, output, stages):
    if mode not in ('readiness','discuss'):raise ValueError('HOSTED_CAMPAIGN_PREPARATION_ONLY')
    if stages.packet.get('campaign_artifacts')!={'version':1,'experiment':'P001','mode':mode}:
        raise ValueError('HOSTED_CAMPAIGN_PACKET_CONTRACT')
    return execute(sc,mode,'P001',request,output,max_rounds=1,stage_runner=stages,
                   initiator={'kind':'agent','family':'codex','model':'gpt-6-astra',
                              'route':'protected-hosted-campaign-v1'})
