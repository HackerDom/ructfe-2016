#!/usr/bin/env python3

import time
import uuid
import random
import string
import requests as r

from httpchecker import *

GET = 'GET'
POST = 'POST'

class Checker(HttpCheckerBase):
	def session(self, addr):
		s = r.Session()
		s.headers['User-Agent'] = 'Robot/0.1 (non-compatible)'
		return s

	def url(self, addr, suffix):
		return 'http://{}{}'.format(addr, suffix)

	def parseresponse(self, response, path):
		try:
			if response.status_code != 200:
				queryPos = path.find('?')
				raise HttpWebException(response.status_code, path[queryPos] if queryPos != -1 else '')
			try:
				result = response.json()
				#self.debug(result)
				return result
			except ValueError:
				self.debug(traceback.format_exc())
				raise r.exceptions.HTTPError('failed to parse response')
		finally:
			response.close()

	def parsestringresponse(self, response, path):
		try:
			if response.status_code != 200:
				raise HttpWebException(response.status_code, path)
			result = response.text
			return result
		finally:
			response.close()

	def jpost(self, s, addr, suffix, data=None):
		response = s.post(self.url(addr, suffix), data=data, timeout=5)
		return self.parseresponse(response, suffix)

	def spost(self, s, addr, suffix, data=None):
		response = s.post(self.url(addr, suffix), data=data, timeout=5)
		return self.parsestringresponse(response, suffix)

	def jget(self, s, addr, suffix, data=None):
		response = s.get(self.url(addr, suffix), params=data, timeout=5)
		return self.parseresponse(response, suffix)

	def sget(self, s, addr, suffix, data=None):
		response = s.get(self.url(addr, suffix), params=data, timeout=5)
		return self.parsestringresponse(response, suffix)

	def randword(self):
		word = ''
		rnd = random.randrange(2,10)
		for i in range(rnd):
			word += random.choice(string.ascii_lowercase)
		return word

	def randphrase(self):
		phrase = ''
		rnd = random.randrange(1,5)
		for i in range(rnd):
			phrase += ' ' + self.randword();
		return phrase.lstrip()

	def randfreqengword(self):
		return random.choice([
			'the','of','and','to','a','in','is','you','are','for','that','or','it','as','be','on','your','with','can',
			'have','this','an','by','not','but','at','from','I','they','more','will','if','some','there','what','about',
			'which','when','one','their','all','also','how','many','do','has','most','people','other','time','so','was',
			'we','these','may','like','use','into','than','up','out','who','them','make','because','such','through','get',
			'work','even','different','its','no','our','new','film','just','only','see','used','good','water','been','need',
			'should','very','any','history','often','way','well','art','know','were','then','my','first','would','money',
			'each','over','world','information','map','find','where','much','take','two','want','important','family',
			'those','example','while','he','look','government','before','help','between','go','own','however','business',
			'us','great','his','being','another','health','same','study','why','few','game','might','think','free','too',
			'had','hi','right','still','system','after','computer','best','must','her','life','since','could','does','now',
			'during','learn','around','usually'
		])

	def randengword(self):
		return random.choice([
			'form','meat','air','day','place','become','number','public','read','keep','part','start','year',
			'every','field','large','once','available','down','give','fish','human','both','local','sure','something','without',
			'come','me','back','better','general','process','she','heat','thanks','specific','enough','long','lot','hand',
			'popular','small','though','experience','include','job','music','person','really','although','thank','book','early',
			'reading','end','method','never','less','play','able','data','feel','high','off','point','type','whether','food',
			'understanding','here','home','certain','economy','little','theory','tonight','law','put','under','value','always',
			'body','common','market','set','bird','guide','provide','change','interest','literature','sometimes','problem','say',
			'next','create','simple','software','state','together','control','knowledge','power','radio','ability','basic','course',
			'economics','hard','add','company','known','love','past','price','size','away','big','internet','possible','television',
			'three','understand','various','yourself','card','difficult','including','list','mind','particular','real','science',
			'trade','consider','either','library','likely','nature','fact','line','product','care','group','idea','risk','several',
			'someone','temperature','united','word','fat','force','key','light','simply','today','training','until','major','name',
			'personal','school','top','current','generally','historical','investment','left','national','amount','level','order',
			'practice','research','sense','service','area','cut','hot','instead','least','natural','physical','piece','show',
			'society','try','check','choose','develop','second','useful','web','activity','boss','short','story','call','industry',
			'last','media','mental','move','pay','sport','thing','actually','against','far','fun','house','let','page','remember',
			'term','test','within','along','answer','increase','oven','quite','scared','single','sound','again','community',
			'definition','focus','individual','matter','safety','turn','everything','kind','quality','soil','ask','board','buy',
			'development','guard','hold','language','later','main','offer','oil','picture','potential','professional','rather',
			'access','additional','almost','especially','garden','international','lower','management','open','player','range','rate',
			'reason','travel','variety','video','week','above','according','cook','determine','future','site','alternative','demand',
			'ever','exercise','following','image','quickly','special','working','case','cause','coast','probably','security','true',
			'whole','action','age','among','bad','boat','country','dance','exam','excuse','grow','movie','organization','record',
			'result','section','across','already','below','building','mouse','allow','cash','class','clear','dry','easy','emotional',
			'equipment','live','nothing','period','physics','plan','store','tax','analysis','cold','commercial','directly','full',
			'involved','itself','low','old','policy','political','purchase','series','side','subject','supply','therefore','thought',
			'basis','boyfriend','deal','direction','mean','primary','space','strategy','technology','worth','army','camera','fall',
			'freedom','paper','rule','similar','stock','weather','yet','bring','chance','environment','everyone','figure','improve',
			'man','model','necessary','positive','produce','search','source','beginning','child','earth','else','healthy','instance',
			'maintain','month','present','program','spend','talk','truth','upset','begin','chicken','close','creative','design',
			'feature','financial','head','marketing','material','medical','purpose','question','rock','salt','tell','themselves',
			'traditional','university','writing','act','article','birth','car','cost','department','difference','dog','drive','exist',
			'federal','goal','green','late','news','object','scale','sun','support','tend','thus','audience','enjoy','entire','fishing',
			'fit','glad','growth','income','marriage','note','perform','profit','proper','related','remove','rent','return','run','speed',
			'strong','style','throughout','user','war','actual','appropriate','bank','combination','complex','content','craft','due',
			'easily','effective','eventually','exactly','failure','half','inside','meaning','medicine','middle','outside','philosophy',
			'regular','reserve','standard','bus','decide','exchange','eye','fast','fire','identify','independent','leave','original',
			'position','pressure','reach','rest','serve','stress','teacher','watch','wide','advantage','beautiful','benefit','box',
			'charge','communication','complete','continue','frame','issue','limited','night','protect','require','significant','step',
			'successful','unless','active','break','chemistry','cycle','disease','disk','electrical','energy','expensive','face',
			'interested','item','metal','nation','negative','occur','paint','pregnant','review','road','role','room','safe','screen',
			'soup','stay','structure','view','visit','visual','write','wrong','account','advertising','affect','ago','anyone','approach',
			'avoid','ball'
		])

	def randlogin(self):
		return random.choice([
			'idiocyxy','x3ajgnk','rs13xtz','zavzema','AssupR','ummubkt','em_inha','xxthin','lovexxve','nagevol',
			'Prahun','zguren','valent','anonik','Boutibi','mitelem','atomiz','etnolo','ze2ta2c','nakrenu',
			'Scheuc','aefoxw','illowqn','gollwn','aldo92','pasjomny','str_ou','magsle','bybelbo','canalet',
			'sabina','br1234','nagica','trzaladh','nosie','lustrou','nullvek','trissa','heynes2r','j3s2tgk',
			'vises1b','maemoto','ata2lap','britne','ysboobspy','tomaiajl','washau','partie','Math20','Ogulink',
			'pvilla','lobos2j','rhagra','pinaybl','aprilbl','humorn','obtahov','agrafat','Entlerf','BPOws',
			'a2p1op','uchelaf','crmdp','mhuinn','cohitar','teampu','opercu','Ladidu','MirmEr','ronee','erDoll',
			'searahlj','g1intjy','Alpenk','Ektrop','Auswuch','frevel','o1kia','iconhav','est_en','Dipnai',
			'surraS','quotex','otasticvz','quecul','trueblo','nde71','brigida','shwoodrx','dreamfo','klopten',
			'ardalh','su_ers','ayayin1n','glitter','Weanna','masiki','elblogd','einsai5w','Pedale','gbvideo',
			'dragon','hotnewsjt','FoumeV','demagog','vojnik','Sernau0h','luydduuf','orabler','paxopsc','wrmbul',
			'letinoe','lobaret','ladyan','madcow','mallet','Elvisi','tenory','angeli','aber1r','t1ar1c','Runtim',
			'Ticenvi','zagabee','wokux','gestor','rezilce','duizel','ma_uzibx','deedee','pinkch','eerios5g',
			'gsusfr','eekdawnu','konfetx','nemiza','klimopb','ko2r1as','joelle','ferrEe','iijoku','apozeug',
			'previsyh','pension','Gaiarsa','Neuans','burrou','ghsman3l','milenim','unapre','dekunci','Dawudte',
			'smutnyrv','monsmo','Domiblo','oria6z','dodawan','torrent','hatedw','aluhim','BopilkT','oola9j',
			'ventver','Simeoli','beibla','deposa','Farbeim','nijemc','ratelafq','wangel','ia777k0','Galesta',
			'o3mundo','lepido','maTTdre','agotar','nakeds','ilencehd','jothep','paiso1u','sjekteap','globoja',
			'pascut_','despar','elegike','agressz','dwarro','wchild','pomeri','maksill','Scibell','Puncovhh',
			'arturo','onorio8','gmit6m','Briesse','kildrx','stebrce','WedLaye','xiaLabxc','tipiciz','Warburg',
			'Moospad','vavasf','NekOth','throww','crogai','groors','eZoog1v','Hurenbo','fuktigty','raspus',
			'bonkalw','varaul','lemoncl','eansepm','Cabrol6b','fdUYse','Aujume','enzo909','halSboy','envadid',
			'flaGka','slAvenk','Rucmanc','CYsNBYN','CVOK2h','z2jmw','entrica','clumsys','hakess','wimberg','ystormqz',
			'rollrgu','rl31zh','naklapa','Penzify','sxxDyb','aby123','marmote','uloviju','encore','crecian',
			'jetlede','eshorsdr','glockech','aid_e1','spainy','Bouswr','areeCorsm','wingts','ang2009s',
			'miseri','aphyn','xliddox','angel2m','Erartoo','heriaf','kilich','garoxb','deplet','wudabum',
			'o2e1maj','Roulett','ashell','eystar','Trnove','Csato0','betisin','timext','urner6v','lurk_mjk',
			'prvobor','Pekten','agulhoa','bancala','ocotla','st4ie6j','Cohesdps','Jozzino','Eltzetj','edumnR',
			'ogdreoms','tandwer','keberi','konzil','xskall','elujahxa1','Szramo','pinksod','a30084','gargui',
			'diSco','discoze','asigna','DemOren','ueDookqr','yeggmh','b_ilar','zasutim','Volksm','Dirmin','wynwynyh',
			'biAllai','odiblegy','secret','tresuts','insuran','wereka','Varvell','nashina','prelud','eroninl',
			'aturdid','przybi','vedric','visuale','dgare','Anagen','Waldtei','fyllili','parsie','Affefly',
			'temy4','maddi6','mshihi','renaren','Gnevsd','Cerigat','jrpanta','mejican','lanosa','thehul','kstoygw',
			'acard','tulpen','bamazeiz','Gezirph','szmerek','atkilus','USAswk','aveusid','Karftwr','rhen21',
			'Edelhe','sklonit','bbosta','premost','Hentze','chente','xblogg','nebhan','stormde','illich',
			'buDlsn','uilogymk','dyftykxu','custodi','rotace2q','spapos','teodsvi','iskrcal','Iantaf','goriSt',
			'oottewu','pe3r2o','mister','newDig','hmarete','friend','lojanoih','Floress','em_li','feblai',
			'Aramee','Pleldce','rdemx0','turjainj','claire','lascauxbd','bankob','nibris9a','quotei','liciouss',
			'angfer','gwmpas','Oppona','camicoxa','magolen','abgegu','nemirni','Attinsv','Bikinic','hollvi',
			'sz3s2rx','Miraga','droitdu','sagev3','toady2','amrantu','Skactw','Steando','dofadeea','exharac',
			'umerilo','guindar','letopi','sars01','odsiewa','Laxaxi','CorsCoi','phasiw','sebanso','papito','solteroj',
			'webpens','ieroul','pup0soj','Gerault','Dymnkey','peDoffi','Algowne','gorigejn','umnini','rompora',
			'misvan','inchex','conger39','Husckov','minciu','thepook','becknay','Thurne','zasipan','fresalyz',
			'lagosp','kesiCa','emuttog','eddyft','ae2pezi','gebutte','glukoza','Pugljem','pembiu','Partita','unanie',
			'Seekan','mal_nge','AR8oy','van300','Caile9w','imaceph','elmKamfn','_otsant','hakutul','imborn','msgpush',
			'ghiono','Scabbio','Azad4o','espadel','itipara','noid13h','K8CTZAE','j0j0fan','elcalv','oinvitab',
			'izmail','ersatzub','perihel','rovovs','seguico','ll_raw','rhodib','Kandora','ariup3t','Musarje',
			'Kindhar','diarej','su_and','gamesii','krypina','drip21lc','fajansa','Saipan3s','scenar','tubrhr',
			'frakti','oporowi','Galfano','miquelc','asals0k','kuransk','rovito6d','ventepr','e3rumqa','istrebi',
			'treui','atupat','Irrara','goca_p','sintagm','bi1laeh','5pawkf','vaginmw','pasCelc','upcakeok',
			'zeefact','severu','crysenc','matresR','Tyncder','card9z','turdide','gewelna','hinzieh','pegreed',
			'ilydaynw','pazaro','comatt','Wicewoo7','ipicaslj','_ehabyuo','heilias','mediasf','erasie','Doonvat',
			'antanow','luxatsu','discoun','longia','darkdi','zagorze','ffiwdal','remira','Santia','vireki','dukinog',
			'aeast','blogmg','greent','Kompasu','skouro','dekadis','go2r1e','predise','exile2','rishig','loiswan',
			'glingsz','zeggeT','espiran','Paulina','mesmots','blogla','dukeblu','e3100tk','veldua0','Engakyc',
			'anny5','protkan','islamo','WibleDu','mDoobej','marcad','sajaste','codothi','ParlFed','aTarieca',
			'Remorin','Cagnol','doceer','seneVe','me_horm04','encres','letst5k','pus1an','desbard','Eleltyz',
			'rudeja','tAffy','xoxoba','bes15h','1JF6W5','namahac_','dakgras','deeltji','Zanoll','ubervo','alyren',
			'Snulle','Kiestra','wilfred','mong24','Jizba2e','decade','rispiglp','sammieb','Fexwoos','uthiwea',
			'rutelk0','migrad','Garitox0','teleti','mitoman','Bellon','thoirh3','krizoji5','elcabo','pengeve',
			'estivat','propiri','chamuy','amosargen','silver','osmotri','il1blqr','kieuhol','odgojn','mybste',
			'Grabela','laminat','brukke','izr_ci','journa','ldexcogi','dekadam','recarga','musivi','gl0var','aubavaqf',
			'lildrum','magurluv','d_rkogr','ande16pw','ruthie','reapud','Baccian','azizaju','yndisle','niedurn',
			'fre_aky','prynceZ','binnetr','Realduc','cels0','Bleifar','Affeldl','eaps00','caitgoe','srarr6i',
			'skater','pokrov','Llangoe','Armeenj','falq_e','rasierqv','Sarasp','anmelde','Falten','aparen','sur3n',
			'filtra','myesca','peroute','mold_o','Prascaf','Franck','cyllell','klargje','iwapoj2','_ymhell','akaofg',
			'rabanh','Osmundw','nazizm3w','Capuni8c','poseerm','noillio','rmem70','oplugt','szaladh','drpsalk6',
			'nomerom','morneg','Aas_und','Geraunz','Minota','fiRehea','zuwette','Lass_g0','lAinemo','utaineaq',
			'club85uk','sachouu','timelip','oscinm','zaPrek','gudangm','dyemeng','shal_a','zingars','orraL',
			'syNge','cha_araj','perche','moronic','whoLehea','comatab','unauctio','dexorsa','kilLick','ambassad',
			'tro0met','sWingleb','bo_cie','hesitant','model','scanties','taeniac','onset','abridgme','sylvine',
			'nonsubtr','cravat','preserve','rennie','lakiest','jibingly','judges','analyse','sKying','precursi',
			'captivat','unme_ll','moravia','warta','cymotric','oveRast','t_ansdes','prudce','xylograp','vulcanis',
			'fusser','diglot','ratEuSes','jodean','sitatung','nilotic','obelise','unde_rog','hydraog','dampish',
			'brink','ovstir','polymeri','radiopaq','baronize','depew','deductib','hemorRa','abyss','price','selma',
			'poniche','pyrenoid','postvent','keLson','eneReti','uneloped','dahna','soyinka','coCklesh','wilton','chalet',
			'ecsc','corrosiv','cunei','jesselto','therm','houSefly','diacylu','outtrave','dravite','ins0nol','sorrento',
			'lebrun','prEbronz','dextra','noadou','stornoWa','non_iti','leapt','hyphenis','wheeze','scrapper','palki',
			'exp_icat','suboma','incused'
		])

	def randendpunct(self):
		return random.choice(['.','!','?','!!!','?!'])

	def randuser(self, randlen):
		login = uuid.uuid4().hex[:randlen]
		passlen = random.randrange(6,10)
		password = uuid.uuid4().hex[:passlen]
		return {'login':self.randlogin() + login, 'pass':password}

	#################
	#     CHECK     #
	#################
	def check(self, addr):
		s = self.session(addr)

		result = self.sget(s, addr, '/')
		if not result or len(result) == 0:
			print('get / failed')
			return EXITCODE_MUMBLE

		return EXITCODE_OK

	#################
	#      PUT      #
	#################
	def put(self, addr, flag_id, flag, vuln):
		s = self.session(addr)

		login = self.randlogin()
		fullName = login.capitalize() + "_" + self.randlogin().capitalize()
		job = self.randengword()
		password = flag_id

		result = self.sget(s, addr, '/login', data={'user':login, 'pass':password})
		if not result:
			print('get /login failed')
			return EXITCODE_MUMBLE

		time.sleep(0.2)

		result = self.sget(s, addr, '/setProfile', data={'fullName': fullName,'job': job, 'notes': flag})
		if not result:
			print('get /setProfile failed')
			return EXITCODE_MUMBLE

		time.sleep(0.2)

		self.debug(login + " " + password)

		return EXITCODE_OK

	#################
	#      GET      #
	#################
	def get(self, addr, flag_id, flag, vuln):
		s = self.session(addr)

		tokens = flag_id.split(' ', 2)
		login = tokens[0]
		password = tokens[1]

		result = self.sget(s, addr, '/login', data={'user':login, 'pass':password})
		if not result:
			print('get /login failed')
			return EXITCODE_MUMBLE

		time.sleep(0.2)

		result = self.sget(s, addr, '/profileForm')
		if result.find(flag) < 0:
			print('flag not found')
			return EXITCODE_CORRUPT

		return EXITCODE_OK

Checker().run()
