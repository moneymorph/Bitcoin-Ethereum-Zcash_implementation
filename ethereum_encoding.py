import json
import time
from keys.ethereum_keys import EthereumWallet

from web3 import Web3, IPCProvider
from web3.middleware import geth_poa_middleware

from eth_account._utils.transactions import ALLOWED_TRANSACTION_KEYS
from eth_account._utils.transactions import serializable_unsigned_transaction_from_dict
from eth_account._utils.signing import extract_chain_id, to_standard_v


etherdelta_abi = json.loads('[{"constant":false,"inputs":[{"name":"tokenGet","type":"address"},{"name":"amountGet","type":"uint256"},{"name":"tokenGive","type":"address"},{"name":"amountGive","type":"uint256"},{"name":"expires","type":"uint256"},{"name":"nonce","type":"uint256"},{"name":"user","type":"address"},{"name":"v","type":"uint8"},{"name":"r","type":"bytes32"},{"name":"s","type":"bytes32"},{"name":"amount","type":"uint256"}],"name":"trade","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"tokenGet","type":"address"},{"name":"amountGet","type":"uint256"},{"name":"tokenGive","type":"address"},{"name":"amountGive","type":"uint256"},{"name":"expires","type":"uint256"},{"name":"nonce","type":"uint256"}],"name":"order","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"bytes32"}],"name":"orderFills","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"tokenGet","type":"address"},{"name":"amountGet","type":"uint256"},{"name":"tokenGive","type":"address"},{"name":"amountGive","type":"uint256"},{"name":"expires","type":"uint256"},{"name":"nonce","type":"uint256"},{"name":"v","type":"uint8"},{"name":"r","type":"bytes32"},{"name":"s","type":"bytes32"}],"name":"cancelOrder","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"name":"depositToken","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"tokenGet","type":"address"},{"name":"amountGet","type":"uint256"},{"name":"tokenGive","type":"address"},{"name":"amountGive","type":"uint256"},{"name":"expires","type":"uint256"},{"name":"nonce","type":"uint256"},{"name":"user","type":"address"},{"name":"v","type":"uint8"},{"name":"r","type":"bytes32"},{"name":"s","type":"bytes32"}],"name":"amountFilled","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"tokens","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"feeMake_","type":"uint256"}],"name":"changeFeeMake","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"feeMake","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"feeRebate_","type":"uint256"}],"name":"changeFeeRebate","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"feeAccount","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"tokenGet","type":"address"},{"name":"amountGet","type":"uint256"},{"name":"tokenGive","type":"address"},{"name":"amountGive","type":"uint256"},{"name":"expires","type":"uint256"},{"name":"nonce","type":"uint256"},{"name":"user","type":"address"},{"name":"v","type":"uint8"},{"name":"r","type":"bytes32"},{"name":"s","type":"bytes32"},{"name":"amount","type":"uint256"},{"name":"sender","type":"address"}],"name":"testTrade","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"feeAccount_","type":"address"}],"name":"changeFeeAccount","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"feeRebate","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"feeTake_","type":"uint256"}],"name":"changeFeeTake","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"admin_","type":"address"}],"name":"changeAdmin","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"token","type":"address"},{"name":"amount","type":"uint256"}],"name":"withdrawToken","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"bytes32"}],"name":"orders","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"feeTake","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"type":"function"},{"constant":false,"inputs":[{"name":"accountLevelsAddr_","type":"address"}],"name":"changeAccountLevelsAddr","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"accountLevelsAddr","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"token","type":"address"},{"name":"user","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"admin","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"tokenGet","type":"address"},{"name":"amountGet","type":"uint256"},{"name":"tokenGive","type":"address"},{"name":"amountGive","type":"uint256"},{"name":"expires","type":"uint256"},{"name":"nonce","type":"uint256"},{"name":"user","type":"address"},{"name":"v","type":"uint8"},{"name":"r","type":"bytes32"},{"name":"s","type":"bytes32"}],"name":"availableVolume","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"inputs":[{"name":"admin_","type":"address"},{"name":"feeAccount_","type":"address"},{"name":"accountLevelsAddr_","type":"address"},{"name":"feeMake_","type":"uint256"},{"name":"feeTake_","type":"uint256"},{"name":"feeRebate_","type":"uint256"}],"payable":false,"type":"constructor"},{"payable":false,"type":"fallback"},{"anonymous":false,"inputs":[{"indexed":false,"name":"tokenGet","type":"address"},{"indexed":false,"name":"amountGet","type":"uint256"},{"indexed":false,"name":"tokenGive","type":"address"},{"indexed":false,"name":"amountGive","type":"uint256"},{"indexed":false,"name":"expires","type":"uint256"},{"indexed":false,"name":"nonce","type":"uint256"},{"indexed":false,"name":"user","type":"address"}],"name":"Order","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"tokenGet","type":"address"},{"indexed":false,"name":"amountGet","type":"uint256"},{"indexed":false,"name":"tokenGive","type":"address"},{"indexed":false,"name":"amountGive","type":"uint256"},{"indexed":false,"name":"expires","type":"uint256"},{"indexed":false,"name":"nonce","type":"uint256"},{"indexed":false,"name":"user","type":"address"},{"indexed":false,"name":"v","type":"uint8"},{"indexed":false,"name":"r","type":"bytes32"},{"indexed":false,"name":"s","type":"bytes32"}],"name":"Cancel","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"tokenGet","type":"address"},{"indexed":false,"name":"amountGet","type":"uint256"},{"indexed":false,"name":"tokenGive","type":"address"},{"indexed":false,"name":"amountGive","type":"uint256"},{"indexed":false,"name":"get","type":"address"},{"indexed":false,"name":"give","type":"address"}],"name":"Trade","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"token","type":"address"},{"indexed":false,"name":"user","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"balance","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"token","type":"address"},{"indexed":false,"name":"user","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"balance","type":"uint256"}],"name":"Withdraw","type":"event"}]')
etherdelta_bytecode = '6060604052341561000c57fe5b60405160c080611a7983398101604090815281516020830151918301516060840151608085015160a090950151929491929091905b60008054600160a060020a03808916600160a060020a0319928316179092556001805488841690831617905560028054928716929091169190911790556003839055600482905560058190555b5050505050505b6119d5806100a46000396000f300606060405236156101385763ffffffff60e060020a6000350416630a19b14a811461014d5780630b9276661461019957806319774d43146101ca578063278b8c0e146101fb5780632e1a7d4d14610239578063338b5dea1461024e57806346be96c31461026f578063508493bc146102c757806354d03b5c146102fb57806357786394146103105780635e1d7ae41461033257806365e17c9d146103475780636c86888b1461037357806371ffcb16146103dc578063731c2f81146103fa5780638823a9c01461041c5780638f283970146104315780639e281a981461044f578063bb5f462914610470578063c281309e146104a3578063d0e30db0146104c5578063e8f6bc2e146104cf578063f3412942146104ed578063f7888aec14610519578063f851a4401461054d578063fb6e155f14610579575b341561014057fe5b61014b5b610000565b565b005b341561015557fe5b61014b600160a060020a0360043581169060243590604435811690606435906084359060a4359060c4351660ff60e435166101043561012435610144356105d1565b005b34156101a157fe5b61014b600160a060020a03600435811690602435906044351660643560843560a435610896565b005b34156101d257fe5b6101e9600160a060020a03600435166024356109a7565b60408051918252519081900360200190f35b341561020357fe5b61014b600160a060020a03600435811690602435906044351660643560843560a43560ff60c4351660e435610104356109c4565b005b341561024157fe5b61014b600435610bd4565b005b341561025657fe5b61014b600160a060020a0360043516602435610cf2565b005b341561027757fe5b6101e9600160a060020a0360043581169060243590604435811690606435906084359060a4359060c4351660ff60e435166101043561012435610e46565b60408051918252519081900360200190f35b34156102cf57fe5b6101e9600160a060020a0360043581169060243516610f33565b60408051918252519081900360200190f35b341561030357fe5b61014b600435610f50565b005b341561031857fe5b6101e9610f83565b60408051918252519081900360200190f35b341561033a57fe5b61014b600435610f89565b005b341561034f57fe5b610357610fc8565b60408051600160a060020a039092168252519081900360200190f35b341561037b57fe5b6103c8600160a060020a0360043581169060243590604435811690606435906084359060a4359060c43581169060ff60e43516906101043590610124359061014435906101643516610fd7565b604080519115158252519081900360200190f35b34156103e457fe5b61014b600160a060020a0360043516611042565b005b341561040257fe5b6101e961107c565b60408051918252519081900360200190f35b341561042457fe5b61014b600435611082565b005b341561043957fe5b61014b600160a060020a03600435166110c1565b005b341561045757fe5b61014b600160a060020a03600435166024356110fb565b005b341561047857fe5b6103c8600160a060020a0360043516602435611299565b604080519115158252519081900360200190f35b34156104ab57fe5b6101e96112b9565b60408051918252519081900360200190f35b61014b6112bf565b005b34156104d757fe5b61014b600160a060020a0360043516611361565b005b34156104f557fe5b61035761139b565b60408051600160a060020a039092168252519081900360200190f35b341561052157fe5b6101e9600160a060020a03600435811690602435166113aa565b60408051918252519081900360200190f35b341561055557fe5b6103576113d7565b60408051600160a060020a039092168252519081900360200190f35b341561058157fe5b6101e9600160a060020a0360043581169060243590604435811690606435906084359060a4359060c4351660ff60e4351661010435610124356113e6565b60408051918252519081900360200190f35b60006002308d8d8d8d8d8d6000604051602001526040518088600160a060020a0316600160a060020a0316606060020a02815260140187600160a060020a0316600160a060020a0316606060020a02815260140186815260200185600160a060020a0316600160a060020a0316606060020a0281526014018481526020018381526020018281526020019750505050505050506020604051808303816000866161da5a03f1151561067e57fe5b50506040805151600160a060020a0388166000908152600760209081528382208383529052919091205490915060ff16806107625750604080517f19457468657265756d205369676e6564204d6573736167653a0a3332000000008152601c8101839052815190819003603c018120600082815260208381018552928401819052835191825260ff891682840152818401889052606082018790529251600160a060020a038a16936001936080808501949193601f198101939281900390910191866161da5a03f1151561074e57fe5b505060206040510351600160a060020a0316145b801561076e5750874311155b80156107a85750600160a060020a03861660009081526008602090815260408083208484529091529020548b906107a5908461162d565b11155b15156107b357610000565b6107c18c8c8c8c8a87611655565b600160a060020a03861660009081526008602090815260408083208484529091529020546107ef908361162d565b600160a060020a03871660009081526008602090815260408083208584529091529020557f6effdda786735d5033bfad5f53e5131abcced9e52be6c507b62d639685fbed6d8c838c8e8d830281151561084457fe5b60408051600160a060020a039687168152602081019590955292851684840152046060830152828a166080830152339290921660a082015290519081900360c00190a15b505050505050505050505050565b60408051600060209182018190528251606060020a600160a060020a0330811682028352808c1682026014840152602883018b90528916026048820152605c8101879052607c8101869052609c81018590529251909260029260bc808301939192829003018186866161da5a03f1151561090c57fe5b5050604080518051600160a060020a03338116600081815260076020908152868220858352815290869020805460ff191660011790558c8316855284018b905290891683850152606083018890526080830187905260a0830186905260c083015291519192507f3f7f2eda73683c21a15f9435af1028c93185b5f1fa38270762dc32be606b3e85919081900360e00190a15b50505050505050565b600860209081526000928352604080842090915290825290205481565b60408051600060209182018190528251606060020a600160a060020a0330811682028352808f1682026014840152602883018e90528c16026048820152605c81018a9052607c8101899052609c81018890529251909260029260bc808301939192829003018186866161da5a03f11515610a3a57fe5b50506040805151600160a060020a0333166000908152600760209081528382208383529052919091205490915060ff1680610b1e5750604080517f19457468657265756d205369676e6564204d6573736167653a0a3332000000008152601c8101839052815190819003603c018120600082815260208381018552928401819052835191825260ff881682840152818401879052606082018690529251600160a060020a033316936001936080808501949193601f198101939281900390910191866161da5a03f11515610b0a57fe5b505060206040510351600160a060020a0316145b1515610b2957610000565b600160a060020a0333811660008181526008602090815260408083208684528252918290208d905581518e851681529081018d9052928b1683820152606083018a90526080830189905260a0830188905260c083019190915260ff861660e083015261010082018590526101208201849052517f1e0b760c386003e9cb9bcf4fcf3997886042859d9b6ed6320e804597fcdb28b0918190036101400190a15b50505050505050505050565b33600160a060020a0316600090815260008051602061198a833981519152602052604090205481901015610c0757610000565b33600160a060020a0316600090815260008051602061198a8339815191526020526040902054610c379082611931565b33600160a060020a0316600081815260008051602061198a8339815191526020526040808220939093559151909183919081818185876185025a03f1925050501515610c8257610000565b600160a060020a033316600081815260008051602061198a8339815191526020908152604080832054815193845291830193909352818301849052606082015290517ff341246adaac6f497bc2a656f546ab9e182111d630394f0c57c710a59a2cb5679181900360800190a15b50565b600160a060020a0382161515610d0757610000565b604080516000602091820181905282517f23b872dd000000000000000000000000000000000000000000000000000000008152600160a060020a0333811660048301523081166024830152604482018690529351938616936323b872dd9360648084019491938390030190829087803b1515610d7f57fe5b60325a03f11515610d8c57fe5b50506040515115159050610d9f57610000565b600160a060020a0380831660009081526006602090815260408083203390941683529290522054610dd0908261162d565b600160a060020a038381166000818152600660209081526040808320339095168084529482529182902085905581519283528201929092528082018490526060810192909252517fdcbc1c05240f31ff3ad067ef1ee35ce4997762752e3a095284754544f4c709d79181900360800190a15b5050565b600060006002308d8d8d8d8d8d6000604051602001526040518088600160a060020a0316600160a060020a0316606060020a02815260140187600160a060020a0316600160a060020a0316606060020a02815260140186815260200185600160a060020a0316600160a060020a0316606060020a0281526014018481526020018381526020018281526020019750505050505050506020604051808303816000866161da5a03f11515610ef557fe5b50506040805151600160a060020a03881660009081526008602090815283822083835290529190912054925090505b509a9950505050505050505050565b600660209081526000928352604080842090915290825290205481565b60005433600160a060020a03908116911614610f6b57610000565b600354811115610f7a57610000565b60038190555b50565b60035481565b60005433600160a060020a03908116911614610fa457610000565b600554811080610fb5575060045481115b15610fbf57610000565b60058190555b50565b600154600160a060020a031681565b600160a060020a03808d16600090815260066020908152604080832093851683529290529081205483901080159061102057508261101d8e8e8e8e8e8e8e8e8e8e6113e6565b10155b151561102e57506000611032565b5060015b9c9b505050505050505050505050565b60005433600160a060020a0390811691161461105d57610000565b60018054600160a060020a031916600160a060020a0383161790555b50565b60055481565b60005433600160a060020a0390811691161461109d57610000565b6004548111806110ae575060055481105b156110b857610000565b60048190555b50565b60005433600160a060020a039081169116146110dc57610000565b60008054600160a060020a031916600160a060020a0383161790555b50565b600160a060020a038216151561111057610000565b600160a060020a03808316600090815260066020908152604080832033909416835292905220548190101561114457610000565b600160a060020a03808316600090815260066020908152604080832033909416835292905220546111759082611931565b600160a060020a03808416600081815260066020908152604080832033909516808452948252808320959095558451810182905284517fa9059cbb0000000000000000000000000000000000000000000000000000000081526004810194909452602484018690529351919363a9059cbb936044808201949293918390030190829087803b151561120257fe5b60325a03f1151561120f57fe5b5050604051511515905061122257610000565b600160a060020a03808316600081815260066020908152604080832033959095168084529482529182902054825193845290830193909352818101849052606082019290925290517ff341246adaac6f497bc2a656f546ab9e182111d630394f0c57c710a59a2cb5679181900360800190a15b5050565b600760209081526000928352604080842090915290825290205460ff1681565b60045481565b33600160a060020a0316600090815260008051602061198a83398151915260205260409020546112ef903461162d565b33600160a060020a0316600081815260008051602061198a8339815191526020908152604080832085905580519283529082019290925234818301526060810192909252517fdcbc1c05240f31ff3ad067ef1ee35ce4997762752e3a095284754544f4c709d79181900360800190a15b565b60005433600160a060020a0390811691161461137c57610000565b60028054600160a060020a031916600160a060020a0383161790555b50565b600254600160a060020a031681565b600160a060020a038083166000908152600660209081526040808320938516835292905220545b92915050565b600054600160a060020a031681565b60006000600060006002308f8f8f8f8f8f6000604051602001526040518088600160a060020a0316600160a060020a0316606060020a02815260140187600160a060020a0316600160a060020a0316606060020a02815260140186815260200185600160a060020a0316600160a060020a0316606060020a0281526014018481526020018381526020018281526020019750505050505050506020604051808303816000866161da5a03f1151561149957fe5b50506040805151600160a060020a038a166000908152600760209081528382208383529052919091205490935060ff168061157d5750604080517f19457468657265756d205369676e6564204d6573736167653a0a3332000000008152601c8101859052815190819003603c018120600082815260208381018552928401819052835191825260ff8b16828401528184018a9052606082018990529251600160a060020a038c16936001936080808501949193601f198101939281900390910191866161da5a03f1151561156957fe5b505060206040510351600160a060020a0316145b80156115895750894311155b1515611598576000935061161c565b600160a060020a03881660009081526008602090815260408083208684529091529020546115c7908e90611931565b600160a060020a03808e166000908152600660209081526040808320938d16835292905220549092508b906115fc908f61194a565b81151561160557fe5b049050808210156116185781935061161c565b8093505b5050509a9950505050505050505050565b600082820161164a8482108015906116455750838210155b611979565b8091505b5092915050565b6000600060006000670de0b6b3a76400006116728660035461194a565b81151561167b57fe5b049350670de0b6b3a76400006116938660045461194a565b81151561169c57fe5b600254919004935060009250600160a060020a03161561177257600254604080516000602091820181905282517f1cbd0519000000000000000000000000000000000000000000000000000000008152600160a060020a038b8116600483015293519390941693631cbd0519936024808301949391928390030190829087803b151561172457fe5b60325a03f1151561173157fe5b505060405151915050600181141561176557670de0b6b3a76400006117588660055461194a565b81151561176157fe5b0491505b8060021415611772578291505b5b600160a060020a03808b16600090815260066020908152604080832033909416835292905220546117ad906117a8878661162d565b611931565b600160a060020a038b81166000908152600660209081526040808320338516845290915280822093909355908816815220546117fb906117f66117f0888661162d565b87611931565b61162d565b600160a060020a038b811660009081526006602090815260408083208b85168452909152808220939093556001549091168152205461184c906117f6611841878761162d565b85611931565b61162d565b600160a060020a03808c166000908152600660208181526040808420600154861685528252808420959095558c84168352908152838220928a1682529190915220546118ac908a61189d8a8961194a565b8115156118a657fe5b04611931565b600160a060020a0389811660009081526006602090815260408083208b851684529091528082209390935533909116815220546118fd908a6118ee8a8961194a565b8115156118f757fe5b0461162d565b600160a060020a03808a16600090815260066020908152604080832033909416835292905220555b50505050505050505050565b600061193f83831115611979565b508082035b92915050565b600082820261164a841580611645575083858381151561196657fe5b04145b611979565b8091505b5092915050565b801515610cef57610000565b5b50560054cdd369e4e8a8515e52ca72ec816c2101831ad1f18bf44102ed171459c9b4f8a165627a7a723058201f5c6afd64915184f48f2f470649fb4e2cba0d79c31de45410dc1c0b6fc0a62f0029'
etherdelta_constructor = '0000000000000000000000001ed014aec47fae44c9e55bac7662c0b78ae617980000000000000000000000001ed014aec47fae44c9e55bac7662c0b78ae6179800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000aa87bee5380000000000000000000000000000000000000000000000000000000000000000000'



class Ethereum():
    def __init__(self, ipcprovider):
        self.w3 = Web3(IPCProvider(ipcprovider))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.w3.eth.defaultAccount = self.w3.eth.accounts[0]

        self.etherdelta_abi = etherdelta_abi
        self.etherdelta_address = '0xd345b5fb0F05c590Fa7Bf2Edcc763e483ECa4a22'
        self.contract = self.w3.eth.contract(address=self.etherdelta_address, abi=self.etherdelta_abi)


    # ==============================================================================================================
    # Encode the challenge data into a ethereum transaction. This function sends two transaction:
    # tx0 is for paying the decoder and tx1 is for sending the challenge data
    # The function takes as input the publickey of the paying address,
    #  challenge data and user private key(in the conf file)
    # ==============================================================================================================
    def tx_encf(self, vk_p, ct_c, user_config_file_path):
        user_config_file = open(user_config_file_path)
        conf = json.load(user_config_file)

        #-------------first step is to func the user's address-------
        self.user_address = self.w3.geth.personal.importRawKey(conf['SK'], 'the-passphrase')  # import the private key of the user to its wallet
        self.user_address = self.w3.toChecksumAddress(self.user_address) # checksum check
        print("User's address: ", self.user_address)
        input("\nfund the user address: {0}\n"
              "For the Rinkeby testnet you can use https://faucet.rinkeby.io/\n"
              "Once funded press enter.\n".format(self.user_address))

        #------------create tx0 for paying the decoder----------------
        print("Creating tx0")
        self.w3.eth.defaultAccount = self.user_address
        self.w3.geth.personal.unlockAccount(self.user_address, "the-passphrase", 1000)  #unlock the private key to send tx
        paying_address = self.w3.toChecksumAddress(EthereumWallet.public_to_address(vk_p))
        print("Paying address: ", paying_address)
        tx_hash = self.w3.eth.sendTransaction({'to': paying_address , 'from': self.user_address, 'value': 30000000000000000}).hex()
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        print("tx0 hash: ", tx_hash)

        # ------------create tx1 for sending challenge data-----------
        print("Creating tx1")
        self.w3.eth.defaultAccount = self.user_address
        self.w3.geth.personal.unlockAccount(self.user_address, "the-passphrase", 1000)
        tx_hash = self.contract.functions.\
            testTrade(self.user_address,       #address tokenGet
                int(ct_c[0:10],16),      #uint amountGet
                self.user_address,           #address tokenGive
                int(ct_c[10:20], 16),     #uint amountGive
                int(ct_c[20:30], 16),    #uint expires
                0,                      #uint nonce
                self.user_address,           #address user
                37,                     #uint8 v
                bytes.fromhex('5f4a68188e7d65c6e77406c871a6452e0e95dc69050538c72f0d64d1043a96fe'), #bytes32 r  #random valid r and s
                bytes.fromhex('4c463100fddda744e07d4455e27efc6157188bb22ce7d6191c5443c0e7380db6'), #bytes32 s
                int(ct_c[30:40], 16),   #uint amount
                self.user_address            #address sender
                ).transact()
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        #txhash= 0xa90dc8e6ef6d64f8598e0f172fcd087d16166e4d6a38086bcbb0293ff4a6bb23
        print("tx1 hash: ", tx_hash)
        print(tx_receipt)
        return tx_receipt['transactionHash']


    # ================================================================================================
    # This function given a tx hash, decodes it and returns the user's public key and ciphertext
    # ================================================================================================
    def tx_decf(self, tx_hash):
        tx_json = self.w3.eth.getTransaction(tx_hash)
        # check the recipient of the tx and check that the function is the testtrade('0x6c86888b')
        if tx_json['to'] != self.etherdelta_address or tx_json['input'][:10] != '0x6c86888b':
            return -1,-1
        try:
            ct_c = tx_json['input'][128:138] + tx_json['input'][256:266] + tx_json['input'][320:330] + tx_json['input'][704:714]
            vk_u = self._public_from_signature(tx_json)
            print("reconstructed ciphertext from tx: ", ct_c)
            print("user's public key from tx: ", vk_u)
            return vk_u, ct_c
        except:
            return -1,-1


    # ================================================================================================
    # Encode the response data into a ethereum transaction.
    # The function takes as input the private key of the paying key (derived from the shared key)
    # and the response data (ciphertext)
    # ================================================================================================
    def tx_encb(self, sk_s, ct_r, txid=None):
        paying_address = self.w3.geth.personal.importRawKey(sk_s, 'the-passphrase')  # add the paying private key to the wallet
        paying_address = self.w3.toChecksumAddress(paying_address)

        #-------send the response transaction and encoding it into a testTrade function------
        print("Creating tx2")
        self.w3.eth.defaultAccount = paying_address
        self.w3.geth.personal.unlockAccount(paying_address, "the-passphrase", 1000)
        tx_hash = self.contract.functions.\
            testTrade(self.user_address,  # address tokenGet
                int(ct_r[0:10], 16),  # uint amountGet
                self.user_address,  # address tokenGive
                int(ct_r[10:20], 16),  # uint amountGive
                int(ct_r[20:30], 16),  # uint expires
                0,  # uint nonce
                paying_address,  # address user
                37,  # uint8 v
                bytes.fromhex('5f4a68188e7d65c6e77406c871a6452e0e95dc69050538c72f0d64d1043a96fe'), # bytes32 r
                bytes.fromhex('4c463100fddda744e07d4455e27efc6157188bb22ce7d6191c5443c0e7380db6'), # bytes32 s
                int(ct_r[30:40], 16),  # uint amount
                paying_address  # address sender
                ).transact()
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        # txhash=0xa68ad35a9279214fc66b53bfaf68713913307de825251db5f97c9d14880aa2e1
        print(tx_receipt)
        print(tx_hash.hex())
        return tx_hash.hex()


    # ================================================================================================
    # Given a block id and an public key of transaction return the encoded data in that transaction
    # ================================================================================================
    def tx_decb(self, block_id, vk_p):
        paying_address = EthereumWallet.public_to_address(vk_p)
        txs = self.get_block_txs(block_id)
        for tx in txs:
            tx_json = self.w3.eth.getTransaction(tx)
            if int(tx_json['from'],16) == int(paying_address,16) and int(tx_json['to'],16) == int(self.etherdelta_address,16):
                ct_r = tx_json['input'][128:138] + tx_json['input'][256:266] + tx_json['input'][320:330] + tx_json['input'][704:714]
                return ct_r
        return None



    # ================================================================================================
    # Given a block id return the hashes of the transactions in that block.
    # ================================================================================================
    def get_block_txs(self, block_id):
        txs_hashes = self.w3.eth.getBlock(block_id)['transactions']  # Get the hash of transactions inside this block
        return txs_hashes


    # ================================================================================================
    # Given an ethereum transaction this function extracts the corresponding public key of tx sender.
    # =================================================================================================
    def _public_from_signature(self, tx):
        s = self.w3.eth.account._keys.Signature(vrs=(to_standard_v(extract_chain_id(tx.v)[1]), self.w3.toInt(tx.r), self.w3.toInt(tx.s)))
        tt = {k: tx[k] for k in ALLOWED_TRANSACTION_KEYS - {'chainId', 'data'}}
        tt['data'] = tx.input
        tt['chainId'] = extract_chain_id(tx.v)[0]
        ut = serializable_unsigned_transaction_from_dict(tt)
        return s.recover_public_key_from_msg_hash(ut.hash()).to_hex()[2:]






# ================================================================================================
# Deploys the etherdelta contract to the testnet
# =================================================================================================
def deploy_contract(ipcprovider, abi_encoding, byte_code):
    w3 = Web3(IPCProvider(ipcprovider))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.eth.defaultAccount = w3.eth.accounts[0]

    etherDelta = w3.eth.contract(abi=abi_encoding, bytecode=byte_code)
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.geth.personal.unlockAccount(w3.eth.accounts[0], "123456", 1000)
    tx_hash = etherDelta.constructor(w3.eth.accounts[0], w3.eth.accounts[0], w3.eth.accounts[0], 0, 0, 0).transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt)
    return tx_receipt



if __name__ == '__main__':
    ipc_provider_path = 'REPLACE WITH PATH TO IPC'
    print("deploy contract")
    deploy_contract(ipc_provider_path, etherdelta_abi, etherdelta_bytecode)

