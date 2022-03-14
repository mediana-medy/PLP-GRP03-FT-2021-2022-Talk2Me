
from SystemCode.conversation.models.strat_blenderbot_small import Model as strat_blenderbot_small
from SystemCode.conversation.models.vanilla_blenderbot_small import Model as vanilla_blenderbot_small

from SystemCode.conversation.models.strat_dialogpt import Model as strat_dialogpt
from SystemCode.conversation.models.vanilla_dialogpt import Model as vanilla_dialogpt

models = {
    
    'vanilla_blenderbot_small': vanilla_blenderbot_small,
    'strat_blenderbot_small': strat_blenderbot_small,
    
    'vanilla_dialogpt': vanilla_dialogpt,
    'strat_dialogpt': strat_dialogpt,
}