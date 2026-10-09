"""Read bounded MSIX metadata from the official endpoint, without installing.

This verifies the manifest of the downloadable object. It does not certify its
signature or authorize activation: those require the complete pinned package.
"""
from __future__ import annotations
import base64, hashlib, json, os, re, struct, subprocess, zlib
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

URL='https://persistent.oaistatic.com/codex-app-prod/ChatGPT-x64.msix'
PUBLISHER='CN=50BDFD77-8903-4850-9FFE-6E8522F64D5B'
SCRIPT=r'''
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
Add-Type -AssemblyName System.Net.Http
$inputData=[Console]::In.ReadToEnd() | ConvertFrom-Json
$handler=[System.Net.Http.HttpClientHandler]::new();$handler.AllowAutoRedirect=$false
$client=[System.Net.Http.HttpClient]::new($handler);$client.Timeout=[TimeSpan]::FromSeconds(12)
$request=[System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Get,'https://persistent.oaistatic.com/codex-app-prod/ChatGPT-x64.msix')
$request.Headers.Range=[System.Net.Http.Headers.RangeHeaderValue]::new([long]$inputData.start,[long]$inputData.end)
$request.Headers.TryAddWithoutValidation('Cache-Control','no-cache') | Out-Null
if($inputData.etag){$request.Headers.TryAddWithoutValidation('If-Match',[string]$inputData.etag) | Out-Null}
$response=$null;$stream=$null
try {
 $response=$client.SendAsync($request,[System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
 if([int]$response.StatusCode -ne 206){throw 'Official endpoint did not return a bounded range'}
 $range=$response.Content.Headers.ContentRange
 if(-not $range -or $range.From -ne $inputData.start -or $range.To -ne $inputData.end -or -not $range.Length){throw 'Content range differs'}
 $count=[long]$inputData.end-[long]$inputData.start+1
 if($count -gt 2097152 -or $response.Content.Headers.ContentLength -ne $count){throw 'Range length differs'}
 $etag=[string]$response.Headers.ETag
 if(-not $etag -or $etag.StartsWith('W/') -or ($inputData.etag -and $inputData.etag -ne $etag)){throw 'Object identity changed'}
 $stream=$response.Content.ReadAsStreamAsync().GetAwaiter().GetResult();$bytes=[byte[]]::new($count);$offset=0
 while($offset -lt $count){$n=$stream.Read($bytes,$offset,$count-$offset);if($n -eq 0){throw 'Incomplete range'};$offset+=$n}
 if($stream.ReadByte() -ne -1){throw 'Overlong range'}
 [ordered]@{etag=$etag;total=$range.Length;bytes=[Convert]::ToBase64String($bytes)} | ConvertTo-Json -Compress
} finally {if($stream){$stream.Dispose()};if($response){$response.Dispose()};$request.Dispose();$client.Dispose();$handler.Dispose()}
'''

class Remote:
    def __init__(self):self.etag=None;self.total=None;self.bytes_read=0
    def read(self,start,count):
        if count<=0 or count>2*1024**2 or start<0 or (self.total is not None and start+count>self.total):raise ValueError('range_bounds')
        if self.bytes_read+count>4*1024**2:raise ValueError('metadata_budget')
        shell=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
        cp=subprocess.run([str(shell),'-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(SCRIPT.encode('utf-16le')).decode()],input=json.dumps({'start':start,'end':start+count-1,'etag':self.etag}),capture_output=True,text=True,encoding='utf8',errors='replace',timeout=20,creationflags=0x08000000)
        if cp.returncode:raise ValueError('range_request_failed')
        value=json.loads(cp.stdout);raw=base64.b64decode(value['bytes'],validate=True)
        if len(raw)!=count:raise ValueError('range_length')
        if not isinstance(value.get('etag'),str) or not re.fullmatch(r'"[^"\r\n]{1,254}"',value['etag']) or type(value.get('total')) is not int or value['total']<start+count:raise ValueError('range_identity')
        if self.etag is not None and (self.etag!=value['etag'] or self.total!=value['total']):raise ValueError('object_changed')
        self.etag=value['etag'];self.total=int(value['total']);self.bytes_read+=count
        if self.bytes_read>4*1024**2:raise ValueError('metadata_budget')
        return raw

def inspect_remote(remote):
    remote.read(0,1)
    count=min(remote.total,65557);start=remote.total-count;tail=remote.read(start,count)
    pos=tail.rfind(b'PK\x05\x06')
    if pos<0 or pos+22>len(tail):raise ValueError('zip_end_missing')
    disk,central_disk,on_disk,total,csize,coffset,comment=struct.unpack_from('<4H2IH',tail,pos+4)
    if disk or central_disk or on_disk!=total or pos+22+comment!=len(tail):raise ValueError('split_or_ambiguous_zip')
    if 65535 in (on_disk,total) or 0xffffffff in (csize,coffset):
        loc=tail[pos-20:pos]
        if len(loc)!=20 or loc[:4]!=b'PK\x06\x07':raise ValueError('zip64_locator')
        ld,offset,disks=struct.unpack_from('<IQI',loc,4)
        if ld or disks!=1:raise ValueError('zip64_disk')
        data=remote.read(offset,56)
        if data[:4]!=b'PK\x06\x06':raise ValueError('zip64_end')
        _,_,disk,central_disk,on_disk,total,csize,coffset=struct.unpack_from('<HHIIQQQQ',data,12)
        if disk or central_disk or on_disk!=total:raise ValueError('zip64_counts')
    if total>50000 or csize>2*1024**2 or coffset+csize>remote.total:raise ValueError('central_bounds')
    central=remote.read(coffset,csize);cursor=0;entries={}
    while cursor<len(central):
        if central[cursor:cursor+4]!=b'PK\x01\x02' or cursor+46>len(central):raise ValueError('central_entry')
        f=struct.unpack_from('<4s6H3I5H2I',central,cursor)
        _,made,needed,flags,method,tm,dt,crc,compressed,size,nlen,elen,clen,disk,attrs,external,offset=f
        end=cursor+46+nlen+elen+clen
        if end>len(central) or disk or flags&1:raise ValueError('central_entry_bounds')
        name=central[cursor+46:cursor+46+nlen].decode('utf8' if flags&0x800 else 'cp437')
        if name in entries:raise ValueError('duplicate_name')
        entries[name]={'flags':flags,'method':method,'crc':crc,'compressed':compressed,'size':size,'offset':offset}
        cursor=end
    if len(entries)!=total or not {'AppxManifest.xml','AppxBlockMap.xml','AppxSignature.p7x'}<=entries.keys():raise ValueError('incomplete_msix')
    row=entries['AppxManifest.xml']
    if row['compressed']>262144 or row['size']>1048576 or row['method']not in (0,8):raise ValueError('manifest_bounds')
    head=remote.read(row['offset'],30)
    if head[:4]!=b'PK\x03\x04':raise ValueError('local_header')
    _,needed,flags,method,tm,dt,crc,csize,size,nlen,elen=struct.unpack('<4s5H3I2H',head)
    if flags!=row['flags'] or method!=row['method']:raise ValueError('header_disagreement')
    data=remote.read(row['offset']+30,nlen+elen+row['compressed'])
    if data[:nlen]!=b'AppxManifest.xml':raise ValueError('local_name')
    content=data[nlen+elen:]
    if method==8:
        decoder=zlib.decompressobj(-15);content=decoder.decompress(content,row['size']+1)
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('deflate_bounds')
    if len(content)!=row['size'] or zlib.crc32(content)!=row['crc']:raise ValueError('manifest_crc')
    if b'\x00' in content or b'<!DOCTYPE' in content.upper() or b'<!ENTITY' in content.upper():raise ValueError('manifest_dtd')
    root=ET.fromstring(content);identity=root.find('{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Identity')
    if identity is None or identity.get('Name')!='OpenAI.Codex' or identity.get('ProcessorArchitecture')!='x64' or identity.get('Publisher')!=PUBLISHER:raise ValueError('manifest_identity')
    version=identity.get('Version','')
    if not re.fullmatch(r'\d{1,5}(?:\.\d{1,5}){3}',version) or any(int(x)>65535 for x in version.split('.')):raise ValueError('manifest_version')
    return {'status':'manifest_verified','identity':'OpenAI.Codex','architecture':'x64','version':version,'publisher':PUBLISHER,'source':URL,'checked_at':datetime.now(timezone.utc).isoformat(),'etag':remote.etag,'package_size':remote.total,'manifest_sha256':hashlib.sha256(content).hexdigest(),'metadata_bytes_read':remote.bytes_read,'complete_signature_verification_pending':True}

def fetch_package():
    try:return inspect_remote(Remote())
    except Exception as exc:return {'status':'unavailable','reason_code':type(exc).__name__,'source':URL,'checked_at':datetime.now(timezone.utc).isoformat()}
