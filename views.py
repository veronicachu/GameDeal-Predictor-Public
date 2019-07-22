from flask import Flask, render_template, request, jsonify
#import __init__
from application import generalFunctions
from application import grabGameImage
from application import runPredictions
from application import grabGamePrice
import datetime

gameTitles = generalFunctions.load_pickleObject('SteamGameTitles')

#Initialize app
#app = Flask(__name__, static_url_path='/static')

#My home page redirects to inputs.html where the user fills out their target game and price
@app.route('/', methods=['GET', 'POST'])
def inputs():
    return render_template('inputs.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    results = [k for k in gameTitles if search in k] # search for exact letters in list
#    results = [mv[0] for mv in query.all()]
    return jsonify(matching_results=results)

#After submit inputs, the input page redirects to predictions.html
@app.route('/predictions', methods=['GET', 'POST'])
def predictions():
    # Gather inputs from input page
    target_game = request.form['game_title']    # Target game input
    target_day = float(request.form['target_day'])  # Target day input
    
    # Get game image and save in local file
    game_url = grabGameImage.grabGameImage(target_game)
    
    # Run models
    # outputs: list([predictedPriceOutput, historicalLow, probDealTomorrow, nextHighProbDay, predictedPriceOutput_prob])
    pricePredictions = runPredictions.predict_gamedeal(target_game, target_day)
    nextHighProbDay = pricePredictions[3]
    
    # Get current price of game on Steam
    currentprice = grabGamePrice.grabGamePrice(target_game)
    if len(currentprice) == 1:
        game_price = ("Game currently at " + currentprice[0])
    elif len == 0:
        game_price = ("Unable to get current price")
    else:
        game_price = ("Game is currently on sale at " + currentprice[0] +
                      " (Regular Price: " + currentprice[1] + ")")
    
    # Transform wait day to ISO date
    calStart_target = datetime.datetime.now() + datetime.timedelta(days=target_day*30)
    calEnd_target = calStart_target + datetime.timedelta(days=1)
    calStart_target = datetime.datetime.strftime(calStart_target, '%Y%m%d')
    calEnd_target = datetime.datetime.strftime(calEnd_target, '%Y%m%d')
    
    # Transform next deal day to ISO date
    calStart_nextdeal = datetime.datetime.now() + datetime.timedelta(days=nextHighProbDay)
    calEnd_nextdeal = calStart_nextdeal + datetime.timedelta(days=1)
    calStart_nextdeal = datetime.datetime.strftime(calStart_nextdeal, '%Y%m%d')
    calEnd_nextdeal = datetime.datetime.strftime(calEnd_nextdeal, '%Y%m%d')
    
    # Polish next deal day for webpage output
    nextHighProbDay= (str(round(nextHighProbDay/30, 1)) + ' months')
    
    return render_template('predictions.html', 
                           targetGame = target_game,
                           targetWait = target_day,
                           predictedPrice=pricePredictions[0], 
                           historicalLow=pricePredictions[1],
                           probDealTomorrow=pricePredictions[2],
                           nextHighProbDay=nextHighProbDay,
                           predictedPrice_prob=pricePredictions[4],
                           game_url=game_url, 
                           game_price=game_price,
                           calStart_target=calStart_target,
                           calEnd_target=calEnd_target,
                           calStart_nextdeal=calStart_nextdeal,
                           calEnd_nextdeal=calEnd_nextdeal)

if __name__ == '__main__':
    #this runs your app locally
#    app.run(debug=True)
    app.run(host="0.0.0.0", debug=True)