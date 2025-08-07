var stripe = stripe('sk_test_51MZvCeJh1JJwaJ0btlGhnoOmlccrmTi0L5daGLr7tCKuFMdpsLzCa2HAuYlbW5FiiLPmOonyFETCRFnXA39Yqqfo000rF8d1rA')

var elem = document.getElementById('submit');
clientsecret =  elem.getAttribute('data-secret');

var elements = stripe.elements();
var style = {
    base:{
        color: "000",
        lineHeight: '2.4',
        fontSize: '16px'
    }
};
var card = elements.create("card", { style: style });
card.mount("#card-element");


card.on('change', function(event){
    var displayError = document.getElementById('card-errors')
    if (event.error){
        displayError.textContent = event.error.message;
        $('#card-errors').addClass('alert alert-info');
    }else{
        displayError.textContent = '';
        $('#card-errors').removeClass('alert alert-info');
    }
});

var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev){
    ev.preventDefault();

var custName = document.getElementById("custName").value;
var custAddress = document.getElementById("custAddress").value;
var custName = document.getElementById("custName").value;

$ajax({
    type: "POST",
    url: 'http://127.0.0.1:8000?/orders/add',
    data: {
        order_key: clientsecret,
        csrfmiddlewaretoken: CSRF_TOKEN,
        action: "post",
    },
    success: function(json){
        console.log(json.success)

        stripe.confirmCardPayment(clientsecret,{

            payment_method:{
                card: card,
                billing_details:{
                    address:{
                        line1:custAddress,
                        line2:custAdd2
                    },
                    name:custName
                },
            },
        }).then(function(result){
            if(result.error){
                console.log('payment error')
                console.log('pvyment processed')    
            }else{
                if(result.paymentIntent.status === 'succed'){
                    console.log('payment processed')
        
                    window.location.replace("http://127.0.0.1:800/payment/orderplaced")
                }
            }
        
        
        // error: function (xhr, errmsg, err){
        
        // }
        })
    }
})
})