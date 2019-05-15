package com.comp6239.Tutor;

import android.content.Context;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.widget.GridLayoutManager;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import com.comp6239.Backend.BackendRequestController;
import com.comp6239.Backend.Messaging.MessageThread;
import com.comp6239.R;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * A fragment representing a list of Items.
 * <p/>
 * Activities containing this fragment MUST implement the {@link OnSearchStudentFragmentInteractionListener}
 * interface.
 */
public class TutorStudentRequestsFragment extends Fragment {

    // TODO: Customize parameter argument names
    private static final String ARG_COLUMN_COUNT = "column-count";
    // TODO: Customize parameters
    private int mColumnCount = 1;
    private OnSearchStudentFragmentInteractionListener mListener;
    private BackendRequestController apiBackend;
    private RecyclerView mRecyclerView;

    /**
     * Mandatory empty constructor for the fragment manager to instantiate the
     * fragment (e.g. upon screen orientation changes).
     */
    public TutorStudentRequestsFragment() {
    }

    // TODO: Customize parameter initialization
    @SuppressWarnings("unused")
    public static TutorStudentRequestsFragment newInstance(int columnCount) {
        TutorStudentRequestsFragment fragment = new TutorStudentRequestsFragment();
        Bundle args = new Bundle();
        args.putInt(ARG_COLUMN_COUNT, columnCount);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        apiBackend = BackendRequestController.getInstance(getContext());

        if (getArguments() != null) {
            mColumnCount = getArguments().getInt(ARG_COLUMN_COUNT);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_conversation_list, container, false);

        // Set the adapter
        Context context = view.getContext();
        mRecyclerView = (RecyclerView) view;
        if (mColumnCount <= 1) {
            mRecyclerView.setLayoutManager(new LinearLayoutManager(context));
        } else {
            mRecyclerView.setLayoutManager(new GridLayoutManager(context, mColumnCount));
        }
        refreshStudentList();

        return view;
    }

    public void refreshStudentList() {
        Call<List<MessageThread>> tutorList = apiBackend.apiService.getTutorsStudentRequests();
        tutorList.enqueue(new Callback<List<MessageThread>>() {
            @Override
            public void onResponse(Call<List<MessageThread>> call, Response<List<MessageThread>> response) {

                mRecyclerView.setAdapter(new StudentRequestRecyclerViewAdapter(response.body(), mListener));

            }

            @Override
            public void onFailure(Call<List<MessageThread>> call, Throwable t) {
                Toast toast = Toast.makeText(getContext(), "There was a network error searching for student requests! Try again later!", Toast.LENGTH_LONG);
                toast.show();
            }
        });
    }


    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        if (context instanceof OnSearchStudentFragmentInteractionListener) {
            mListener = (OnSearchStudentFragmentInteractionListener) context;
        } else {
            throw new RuntimeException(context.toString()
                    + " must implement OnMyTutorsFragmentInteractionListener");
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        mListener = null;
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p/>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnSearchStudentFragmentInteractionListener {
        void onSearchStudentFragmentInteraction(MessageThread item);
    }
}
